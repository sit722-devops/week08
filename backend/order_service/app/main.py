import logging
import os
import sys
import time
from decimal import Decimal
from typing import List, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Order, OrderItem
from .schemas import OrderCreate, OrderItemResponse, OrderResponse

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

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8000")
logger.info(
    "Order Service: Configured to communicate with Product Service at: %s",
    PRODUCT_SERVICE_URL,
)

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Order Service API",
    description="Manages orders for mini-ecommerce app, with synchronous stock deduction.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict for production
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
                "Order Service: Attempting to connect to PostgreSQL and create tables (attempt %s/%s)...",
                i + 1,
                max_retries,
            )
            Base.metadata.create_all(bind=engine)
            logger.info("Order Service: Successfully connected to PostgreSQL and ensured tables exist.")
            break
        except OperationalError as e:
            logger.warning("Order Service: Failed to connect to PostgreSQL: %s", e)
            if i < max_retries - 1:
                logger.info("Order Service: Retrying in %s seconds...", retry_delay_seconds)
                time.sleep(retry_delay_seconds)
            else:
                logger.critical(
                    "Order Service: Failed to connect to PostgreSQL after %s attempts. Exiting application.",
                    max_retries,
                )
                sys.exit(1)
        except Exception as e:
            logger.critical(
                "Order Service: An unexpected error occurred during database startup: %s",
                e,
                exc_info=True,
            )
            sys.exit(1)


# --- Root Endpoint ---
@app.get("/", status_code=status.HTTP_200_OK, summary="Root endpoint")
async def read_root():
    return {"message": "Welcome to the Order Service!"}


# --- Health Check Endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK, summary="Health check endpoint")
async def health_check():
    return {"status": "ok", "service": "order-service"}


@app.post(
    "/orders/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if not order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item.",
        )

    successfully_deducted_items: List[OrderItem] = []
    logger.info("Order Service: Creating new order for user_id: %s", order.user_id)

    async with httpx.AsyncClient() as client:
        for item in order.items:
            product_id = item.product_id
            quantity = item.quantity

            deduct_stock_url = f"{PRODUCT_SERVICE_URL}/products/{product_id}/deduct-stock"
            logger.info(
                "Order Service: Attempting to deduct stock for product %s (qty: %s) via %s",
                product_id,
                quantity,
                deduct_stock_url,
            )
            try:
                response = await client.patch(
                    deduct_stock_url,
                    json={"quantity_to_deduct": quantity},
                    timeout=5,
                )
                response.raise_for_status()
                logger.info("Order Service: Stock deduction successful for product %s.", product_id)
                successfully_deducted_items.append(item)

            except httpx.HTTPStatusError as e:
                error_detail = "Unknown error during stock deduction."
                if e.response.status_code == status.HTTP_404_NOT_FOUND:
                    error_detail = f"Product {product_id} not found."
                elif e.response.status_code == status.HTTP_400_BAD_REQUEST:
                    response_json = e.response.json()
                    error_detail = response_json.get("detail", "Insufficient stock or invalid request.")

                logger.error(
                    "Order Service: Stock deduction failed for product %s: %s. Status: %s",
                    product_id,
                    error_detail,
                    e.response.status_code,
                )
                await _rollback_stock_deductions(client, successfully_deducted_items)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to deduct stock for product {product_id}: {error_detail}",
                )
            except httpx.RequestError as e:
                logger.critical(
                    "Order Service: Network error communicating with Product Service for product %s: %s",
                    product_id,
                    e,
                )
                await _rollback_stock_deductions(client, successfully_deducted_items)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Product Service is currently unavailable. Please try again later. Error: {e}",
                )
            except Exception as e:
                logger.error(
                    "Order Service: Unexpected error during stock deduction for product %s: %s",
                    product_id,
                    e,
                    exc_info=True,
                )
                await _rollback_stock_deductions(client, successfully_deducted_items)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"An unexpected error occurred during order creation: {e}",
                )

    logger.info("Order Service: All product stock deductions successful. Proceeding to create order.")

    total_amount = sum(
        Decimal(str(item.quantity)) * Decimal(str(item.price_at_purchase)) for item in order.items
    )

    db_order = Order(
        user_id=order.user_id,
        shipping_address=order.shipping_address,
        total_amount=total_amount,
        status="pending",
    )

    db.add(db_order)
    db.flush()

    for item in order.items:
        db_order_item = OrderItem(
            order_id=db_order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase,
            item_total=Decimal(str(item.quantity)) * Decimal(str(item.price_at_purchase)),
        )
        db.add(db_order_item)

    try:
        db_order.status = "confirmed"
        db.commit()
        db.refresh(db_order)
        db.add(db_order)
        db.refresh(db_order, attribute_names=["items"])
        logger.info(
            "Order Service: Order %s created and confirmed successfully for user %s.",
            db_order.order_id,
            db_order.user_id,
        )
        return db_order
    except Exception as e:
        db.rollback()
        logger.error("Order Service: Error creating order after successful stock deductions: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order created but failed to save to database. Manual intervention required.",
        )


async def _rollback_stock_deductions(client: httpx.AsyncClient, items: List[OrderItem]):
    if not items:
        return

    logger.warning(
        "Order Service: Attempting to rollback stock deductions due to order creation failure."
    )
    for item in items:
        product_id = item.product_id
        quantity = item.quantity
        # NOTE: We purposefully don't call Product Service here (no compensating API).
        logger.warning(
            "Order Service: Cannot automatically rollback stock for product %s quantity %s. "
            "Manual stock adjustment may be required in Product Service.",
            product_id,
            quantity,
        )


@app.get("/orders/", response_model=List[OrderResponse], summary="Retrieve a list of all orders")
def list_orders(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[int] = Query(None, ge=1, description="Filter orders by user ID."),
    status: Optional[str] = Query(None, max_length=50, description="Filter orders by status (e.g., pending, shipped)."),
):
    logger.info(
        "Order Service: Listing orders (skip=%s, limit=%s, user_id=%s, status='%s')",
        skip,
        limit,
        user_id,
        status,
    )
    query = db.query(Order)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)

    orders = query.offset(skip).limit(limit).all()
    logger.info("Order Service: Retrieved %s orders.", len(orders))
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse, summary="Retrieve a single order by ID")
def get_order(order_id: int, db: Session = Depends(get_db)):
    logger.info("Order Service: Fetching order with ID: %s", order_id)
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        logger.warning("Order Service: Order with ID %s not found.", order_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    logger.info("Order Service: Retrieved order with ID %s. Status: %s", order_id, order.status)
    return order


@app.patch("/orders/{order_id}/status", response_model=OrderResponse, summary="Update the status of an order")
async def update_order_status(
    order_id: int,
    new_status: str = Query(..., min_length=1, max_length=50, description="New status for the order."),
    db: Session = Depends(get_db),
):
    logger.info("Order Service: Updating status for order %s to '%s'", order_id, new_status)
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if not db_order:
        logger.warning("Order Service: Order with ID %s not found for status update.", order_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    db_order.status = new_status

    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info("Order Service: Order %s status updated to '%s'.", order_id, new_status)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error("Order Service: Error updating status for order %s: %s", order_id, e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update order status.")


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an order by ID")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    logger.info("Order Service: Attempting to delete order with ID: %s", order_id)
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        logger.warning("Order Service: Order with ID: %s not found for deletion.", order_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    try:
        db.delete(order)
        db.commit()
        logger.info("Order Service: Order (ID: %s) deleted successfully.", order_id)
    except Exception as e:
        db.rollback()
        logger.error("Order Service: Error deleting order %s: %s", order_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the order.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/orders/{order_id}/items", response_model=List[OrderItemResponse], summary="Retrieve all items for an order")
def get_order_items(order_id: int, db: Session = Depends(get_db)):
    logger.info("Order Service: Fetching items for order ID: %s", order_id)
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        logger.warning("Order Service: Order with ID %s not found when fetching items.", order_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    logger.info("Order Service: Retrieved %s items for order %s.", len(order.items), order_id)
    return order.items
