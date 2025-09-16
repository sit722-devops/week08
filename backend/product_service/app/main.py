import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Optional

# Azure Storage Imports
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)
from fastapi import Depends, FastAPI, File, HTTPException, Query, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Product
from .schemas import ProductCreate, ProductResponse, ProductUpdate, StockDeductRequest

# --- Standard Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Suppress noisy logs from third-party libraries for cleaner output
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "product-images")
AZURE_SAS_TOKEN_EXPIRY_HOURS = int(os.getenv("AZURE_SAS_TOKEN_EXPIRY_HOURS", "24"))

# Initialize BlobServiceClient
if AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY:
    try:
        blob_service_client = BlobServiceClient(
            account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
            credential=AZURE_STORAGE_ACCOUNT_KEY,
        )
        logger.info("Product Service: Azure BlobServiceClient initialized.")
        try:
            container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
            container_client.create_container()
            logger.info("Product Service: Azure container '%s' ensured to exist.", AZURE_STORAGE_CONTAINER_NAME)
        except Exception as e:
            logger.warning(
                "Product Service: Could not create or verify Azure container '%s'. It might already exist. Error: %s",
                AZURE_STORAGE_CONTAINER_NAME,
                e,
            )
    except Exception as e:
        logger.critical(
            "Product Service: Failed to initialize Azure BlobServiceClient. Check credentials/account name. Error: %s",
            e,
            exc_info=True,
        )
        blob_service_client = None
else:
    logger.warning(
        "Product Service: Azure Storage credentials not found. Image upload functionality will be disabled."
    )
    blob_service_client = None


RESTOCK_THRESHOLD = 5

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Product Service API",
    description="Manages products and stock for mini-ecommerce app, with Azure Storage integration.",
    version="1.0.0",
)

# Enable CORS (for frontend dev/testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- FastAPI Event Handlers ---
@app.on_event("startup")
async def startup_event():
    max_retries = 10
    retry_delay_seconds = 5
    for i in range(max_retries):
        try:
            logger.info(
                "Product Service: Attempting to connect to PostgreSQL and create tables (attempt %s/%s)...",
                i + 1,
                max_retries,
            )
            Base.metadata.create_all(bind=engine)
            logger.info("Product Service: Successfully connected to PostgreSQL and ensured tables exist.")
            break
        except OperationalError as e:
            logger.warning("Product Service: Failed to connect to PostgreSQL: %s", e)
            if i < max_retries - 1:
                logger.info("Product Service: Retrying in %s seconds...", retry_delay_seconds)
                time.sleep(retry_delay_seconds)
            else:
                logger.critical(
                    "Product Service: Failed to connect to PostgreSQL after %s attempts. Exiting application.",
                    max_retries,
                )
                sys.exit(1)
        except Exception as e:
            logger.critical("Product Service: Unexpected error during DB startup: %s", e, exc_info=True)
            sys.exit(1)


# --- Root Endpoint ---
@app.get("/", status_code=status.HTTP_200_OK, summary="Root endpoint")
async def read_root():
    return {"message": "Welcome to the Product Service!"}


# --- Health Check Endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK, summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "service": "product-service"}


@app.post(
    "/products/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    logger.info("Product Service: Creating product: %s", product.name)
    try:
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info("Product Service: Product '%s' (ID: %s) created successfully.", db_product.name, db_product.product_id)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error("Product Service: Error creating product: %s", e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create product.")


@app.get("/products/", response_model=List[ProductResponse], summary="Retrieve a list of all products")
def list_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=255),
):
    logger.info("Product Service: Listing products with skip=%s, limit=%s, search='%s'", skip, limit, search)
    query = db.query(Product)
    if search:
        search_pattern = f"%{search}%"
        logger.info("Product Service: Applying search filter for term: %s", search)
        query = query.filter((Product.name.ilike(search_pattern)) | (Product.description.ilike(search_pattern)))
    products = query.offset(skip).limit(limit).all()
    logger.info("Product Service: Retrieved %s products (skip=%s, limit=%s).", len(products), skip, limit)
    return products


@app.get("/products/{product_id}", response_model=ProductResponse, summary="Retrieve a single product by ID")
def get_product(product_id: int, db: Session = Depends(get_db)):
    logger.info("Product Service: Fetching product with ID: %s", product_id)
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        logger.warning("Product Service: Product with ID %s not found.", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    logger.info("Product Service: Retrieved product with ID %s. Name: %s", product_id, product.name)
    return product


@app.put("/products/{product_id}", response_model=ProductResponse, summary="Update an existing product by ID")
async def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    logger.info(
        "Product Service: Updating product %s with data: %s",
        product_id,
        product.model_dump(exclude_unset=True),
    )
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        logger.warning("Product Service: Attempted to update non-existent product with ID %s.", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info("Product Service: Product %s updated successfully.", product_id)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error("Product Service: Error updating product %s: %s", product_id, e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update product.")


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a product by ID")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    logger.info("Product Service: Attempting to delete product with ID: %s", product_id)
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        logger.warning("Product Service: Attempted to delete non-existent product with ID %s.", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    try:
        db.delete(product)
        db.commit()
        logger.info("Product Service: Product %s deleted successfully. Name: %s", product_id, product.name)
    except Exception as e:
        db.rollback()
        logger.error("Product Service: Error deleting product %s: %s", product_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the product.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/products/{product_id}/upload-image",
    response_model=ProductResponse,
    summary="Upload an image for a product to Azure Blob Storage",
)
async def upload_product_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not blob_service_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured or available.",
        )

    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        logger.warning("Product Service: Product with ID %s not found for image upload.", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    allowed_content_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only {', '.join(allowed_content_types)} are allowed.",
        )

    try:
        file_extension = os.path.splitext(file.filename)[1] if os.path.splitext(file.filename)[1] else ".jpg"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        blob_name = f"{timestamp}{file_extension}"

        blob_client = blob_service_client.get_blob_client(
            container=AZURE_STORAGE_CONTAINER_NAME,
            blob=blob_name,
        )

        logger.info(
            "Product Service: Uploading image '%s' for product %s as '%s' to Azure.",
            file.filename,
            product_id,
            blob_name,
        )

        blob_client.upload_blob(
            file.file,
            overwrite=True,
            content_settings=ContentSettings(content_type=file.content_type),
        )

        sas_token = generate_blob_sas(
            account_name=AZURE_STORAGE_ACCOUNT_NAME,
            account_key=AZURE_STORAGE_ACCOUNT_KEY,
            container_name=AZURE_STORAGE_CONTAINER_NAME,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=AZURE_SAS_TOKEN_EXPIRY_HOURS),
        )
        image_url = f"{blob_client.url}?{sas_token}"

        db_product.image_url = image_url
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        logger.info("Product Service: Image uploaded and product %s updated with SAS URL.", product_id)
        return db_product

    except Exception as e:
        db.rollback()
        logger.error("Product Service: Error uploading image for product %s: %s", product_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload image or update product: {e}",
        )


@app.patch(
    "/products/{product_id}/deduct-stock",
    response_model=ProductResponse,
    summary="Deduct stock quantity for a product",
)
async def deduct_product_stock(product_id: int, request: StockDeductRequest, db: Session = Depends(get_db)):
    logger.info(
        "Product Service: Attempting to deduct %s from stock for product ID: %s",
        request.quantity_to_deduct,
        product_id,
    )
    db_product = db.query(Product).filter(Product.product_id == product_id).first()

    if not db_product:
        logger.warning("Product Service: Stock deduction failed: product %s not found.", product_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if db_product.stock_quantity < request.quantity_to_deduct:
        logger.warning(
            "Product Service: Stock deduction failed for product %s. Insufficient stock: %s available, %s requested.",
            product_id,
            db_product.stock_quantity,
            request.quantity_to_deduct,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product '{db_product.name}'. Only {db_product.stock_quantity} available.",
        )

    db_product.stock_quantity -= request.quantity_to_deduct

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(
            "Product Service: Stock for product %s updated to %s. Deducted %s.",
            product_id,
            db_product.stock_quantity,
            request.quantity_to_deduct,
        )
        if db_product.stock_quantity < RESTOCK_THRESHOLD:
            logger.warning(
                "Product Service: ALERT! Stock for '%s' (ID: %s) is low: %s.",
                db_product.name,
                db_product.product_id,
                db_product.stock_quantity,
            )
        return db_product
    except Exception as e:
        db.rollback()
        logger.error("Product Service: Error deducting stock for product %s: %s", product_id, e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not deduct stock.")