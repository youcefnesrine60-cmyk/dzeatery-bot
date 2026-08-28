# ==============================================
# 📦 ORDERS API
# نقاط نهاية API للطلبات
# تدير عمليات إنشاء واستعراض وتحديث وحذف الطلبات
# ==============================================

from typing import (
    List,
    Optional,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logger import logger
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    OrderSummary,
    OrderUpdate,
    OrderWithItemsResponse,
)
from app.services.business.orders import (
    add_item_to_order,
    cancel_order,
    change_order_status,
    complete_order,
    create_restaurant_order,
    get_order_items_list,
    get_order_with_details,
    get_orders,
    get_orders_by_status,
    get_restaurant_order,
    mark_order_paid,
    remove_order,
    remove_item_from_order,
)

# ==============================================
# 🧩 TYPES
# ==============================================

OrderList = List[OrderResponse]

# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

# ==============================================
# 📋 ENDPOINTS
# ==============================================

# ==============================================
# LIST ORDERS
# ==============================================

@router.get(
    "/",
    response_model=OrderList,
    summary="قائمة الطلبات",
    description="الحصول على قائمة الطلبات مع إمكانية التصفية",
)
async def list_orders(
    *,
    restaurant_id: Optional[int] = Query(
        None,
        description="معرف المطعم",
    ),
    status: Optional[str] = Query(
        None,
        description="حالة الطلب",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="عدد السجلات للتخطي",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="الحد الأقصى للسجلات",
    ),
    session: AsyncSession = Depends(get_db),
) -> OrderList:
    """
    الحصول على قائمة الطلبات.
    
    Args:
        restaurant_id: معرف المطعم للتصفية
        status: حالة الطلب للتصفية
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        قائمة الطلبات
    """
    logger.info(
        "api_list_orders",
        extra={
            "restaurant_id": restaurant_id,
            "status": status,
            "skip": skip,
            "limit": limit,
        },
    )

    if restaurant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="restaurant_id is required",
        )

    if status is not None:
        orders = await get_orders_by_status(
            restaurant_id=restaurant_id,
            status=status,
            session=session,
            skip=skip,
            limit=limit,
        )
    else:
        orders = await get_orders(
            restaurant_id=restaurant_id,
            session=session,
            skip=skip,
            limit=limit,
        )

    return [
        OrderResponse.model_validate(order)
        for order in orders
    ]


# ==============================================
# GET ORDER BY ID
# ==============================================

@router.get(
    "/{order_id}",
    response_model=OrderWithItemsResponse,
    summary="طلب بالمعرف",
    description="الحصول على طلب محدد مع جميع تفاصيله",
)
async def get_order(
    *,
    order_id: int,
    session: AsyncSession = Depends(get_db),
) -> OrderWithItemsResponse:
    """
    الحصول على طلب بالمعرف مع جميع تفاصيله.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب مع جميع تفاصيله
        
    Raises:
        HTTPException: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "api_get_order",
        extra={"order_id": order_id},
    )

    # جلب الطلب مع العلاقات
    order = await get_order_with_details(
        order_id=order_id,
        session=session,
    )

    if not order:
        logger.warning(
            "api_order_not_found",
            extra={"order_id": order_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # جلب عناصر الطلب
    items = await get_order_items_list(
        order_id=order_id,
        session=session,
    )

    # بناء الاستجابة
    response = OrderWithItemsResponse.model_validate(order)
    response.items = [item.to_dict() for item in items] if items else []

    return response


# ==============================================
# CREATE ORDER
# ==============================================

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء طلب",
    description="إنشاء طلب جديد",
)
async def create_order(
    *,
    data: OrderCreate,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    إنشاء طلب جديد.
    
    Args:
        data: بيانات الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المنشأ
    """
    logger.info(
        "api_create_order",
        extra={
            "restaurant_id": data.restaurant_id,
            "order_type": data.order_type,
        },
    )

    # إنشاء الطلب
    order_id = await create_restaurant_order(
        restaurant_id=data.restaurant_id,
        branch_id=data.branch_id,
        table_id=data.table_id,
        employee_id=data.employee_id,
        order_number="",  # سيتم توليده تلقائياً
        order_type=data.order_type,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        customer_note=data.customer_note,
        subtotal_amount=data.subtotal_amount,
        discount_amount=data.discount_amount,
        tax_amount=data.tax_amount,
        delivery_amount=data.delivery_amount,
        total_amount=data.total_amount,
        session=session,
    )

    # إضافة عناصر الطلب
    if data.items:
        for item in data.items:
            await add_item_to_order(
                order_id=order_id,
                product_id=item["product_id"],
                product_name=item["product_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
                total_price=item["total_price"],
                options=item.get("options"),
                session=session,
            )

    # جلب الطلب المنشأ
    order = await get_restaurant_order(
        order_id=order_id,
        session=session,
    )

    return OrderResponse.model_validate(order)


# ==============================================
# UPDATE ORDER
# ==============================================

@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="تحديث طلب",
    description="تحديث طلب موجود",
)
async def update_order(
    *,
    order_id: int,
    data: OrderUpdate,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    تحديث طلب موجود.
    
    Args:
        order_id: معرف الطلب
        data: بيانات التحديث
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "api_update_order",
        extra={
            "order_id": order_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    # التحقق من وجود الطلب
    order = await get_restaurant_order(
        order_id=order_id,
        session=session,
    )

    if not order:
        logger.warning(
            "api_order_not_found_for_update",
            extra={"order_id": order_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # تحديث الطلب
    from app.repositories.orders_repo import OrdersRepository

    orders_repo = OrdersRepository(session=session)
    update_data = data.model_dump(exclude_unset=True)
    updated_order = await orders_repo.update(
        id=order_id,
        data=update_data,
    )

    return OrderResponse.model_validate(updated_order)


# ==============================================
# UPDATE ORDER STATUS
# ==============================================

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="تحديث حالة الطلب",
    description="تغيير حالة الطلب",
)
async def update_order_status(
    *,
    order_id: int,
    data: OrderStatusUpdate,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    تغيير حالة الطلب.
    
    Args:
        order_id: معرف الطلب
        data: بيانات تحديث الحالة
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "api_update_order_status",
        extra={
            "order_id": order_id,
            "new_status": data.status,
            "employee_id": data.employee_id,
        },
    )

    # التحقق من وجود الطلب
    order = await get_restaurant_order(
        order_id=order_id,
        session=session,
    )

    if not order:
        logger.warning(
            "api_order_not_found_for_status_update",
            extra={"order_id": order_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # تحديث حالة الطلب
    updated_order = await change_order_status(
        order_id=order_id,
        new_status=data.status,
        employee_id=data.employee_id,
        note=data.note,
        session=session,
    )

    return OrderResponse.model_validate(updated_order)


# ==============================================
# COMPLETE ORDER
# ==============================================

@router.post(
    "/{order_id}/complete",
    response_model=OrderResponse,
    summary="إكمال الطلب",
    description="إكمال الطلب (تعيين الحالة إلى completed)",
)
async def complete_order_endpoint(
    *,
    order_id: int,
    employee_id: Optional[int] = Query(
        None,
        description="معرف الموظف",
    ),
    note: Optional[str] = Query(
        None,
        description="ملاحظة",
    ),
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    إكمال الطلب.
    
    Args:
        order_id: معرف الطلب
        employee_id: معرف الموظف (اختياري)
        note: ملاحظة (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المحدث
    """
    logger.info(
        "api_complete_order",
        extra={
            "order_id": order_id,
            "employee_id": employee_id,
        },
    )

    await complete_order(
        order_id=order_id,
        employee_id=employee_id,
        note=note,
        session=session,
    )

    # جلب الطلب المحدث
    order = await get_restaurant_order(
        order_id=order_id,
        session=session,
    )

    return OrderResponse.model_validate(order)


# ==============================================
# CANCEL ORDER
# ==============================================

@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="إلغاء الطلب",
    description="إلغاء الطلب",
)
async def cancel_order_endpoint(
    *,
    order_id: int,
    employee_id: Optional[int] = Query(
        None,
        description="معرف الموظف",
    ),
    reason: Optional[str] = Query(
        None,
        description="سبب الإلغاء",
    ),
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    إلغاء الطلب.
    
    Args:
        order_id: معرف الطلب
        employee_id: معرف الموظف (اختياري)
        reason: سبب الإلغاء (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المحدث
    """
    logger.info(
        "api_cancel_order",
        extra={
            "order_id": order_id,
            "employee_id": employee_id,
            "reason": reason,
        },
    )

    await cancel_order(
        order_id=order_id,
        employee_id=employee_id,
        reason=reason,
        session=session,
    )

    # جلب الطلب المحدث
    order = await get_restaurant_order(
        order_id=order_id,
        session=session,
    )

    return OrderResponse.model_validate(order)


# ==============================================
# MARK ORDER AS PAID
# ==============================================

@router.post(
    "/{order_id}/paid",
    response_model=OrderResponse,
    summary="تحديد الطلب كمدفوع",
    description="تحديد الطلب كمدفوع",
)
async def mark_order_paid_endpoint(
    *,
    order_id: int,
    payment_id: int = Query(
        ...,
        description="معرف الدفعة",
    ),
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    تحديد الطلب كمدفوع.
    
    Args:
        order_id: معرف الطلب
        payment_id: معرف الدفعة
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المحدث
    """
    logger.info(
        "api_mark_order_paid",
        extra={
            "order_id": order_id,
            "payment_id": payment_id,
        },
    )

    await mark_order_paid(
        order_id=order_id,
        payment_id=payment_id,
        session=session,
    )

    # جلب الطلب المحدث
    order = await get_restaurant_order(
        order_id=order_id,
        session=session,
    )

    return OrderResponse.model_validate(order)


# ==============================================
# DELETE ORDER
# ==============================================

@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف طلب",
    description="حذف طلب موجود",
)
async def delete_order(
    *,
    order_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    حذف طلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        HTTPException: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "api_delete_order",
        extra={"order_id": order_id},
    )

    try:
        await remove_order(
            order_id=order_id,
            session=session,
        )

    except ValueError as e:
        logger.warning(
            "api_order_not_found_for_delete",
            extra={
                "order_id": order_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    logger.info(
        "api_order_deleted_successfully",
        extra={"order_id": order_id},
    )


# ==============================================
# GET ORDER SUMMARY
# ==============================================

@router.get(
    "/stats/summary",
    response_model=OrderSummary,
    summary="ملخص الطلبات",
    description="الحصول على ملخص الطلبات لمطعم معين",
)
async def get_order_summary(
    *,
    restaurant_id: int = Query(
        ...,
        description="معرف المطعم",
    ),
    session: AsyncSession = Depends(get_db),
) -> OrderSummary:
    """
    الحصول على ملخص الطلبات.
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        ملخص الطلبات
    """
    logger.info(
        "api_get_order_summary",
        extra={"restaurant_id": restaurant_id},
    )

    # جلب جميع الطلبات
    orders = await get_orders(
        restaurant_id=restaurant_id,
        session=session,
    )

    # حساب الإحصائيات
    status_counts = {}
    total_revenue = 0.0

    for order in orders:
        status = order.status
        status_counts[status] = status_counts.get(status, 0) + 1

        if order.status in ["completed", "delivered", "paid"]:
            total_revenue += order.total_amount

    total_orders = len(orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    return OrderSummary(
        total_orders=total_orders,
        pending_orders=status_counts.get("pending", 0),
        confirmed_orders=status_counts.get("confirmed", 0),
        preparing_orders=status_counts.get("preparing", 0),
        ready_orders=status_counts.get("ready", 0),
        delivering_orders=status_counts.get("delivering", 0),
        delivered_orders=status_counts.get("delivered", 0),
        completed_orders=status_counts.get("completed", 0),
        cancelled_orders=status_counts.get("cancelled", 0),
        total_revenue=total_revenue,
        avg_order_value=avg_order_value,
    )