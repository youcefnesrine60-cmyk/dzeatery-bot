# ==============================================
# 🏭 DATA FACTORIES
# مصانع لإنشاء بيانات الاختبار
# ==============================================


class OwnerFactory:
    """
    مصنع لإنشاء بيانات المالك
    """

    @staticmethod
    def create(
        chat_id: int = 123456789,
        full_name: str = "أحمد محمد",
        phone: str = "0555123456",
        email: str = "ahmed@example.com",
    ) -> dict:
        return {
            "chat_id": chat_id,
            "full_name": full_name,
            "phone": phone,
            "email": email,
        }


class RestaurantFactory:
    """
    مصنع لإنشاء بيانات المطعم
    """

    @staticmethod
    def create(
        owner_id: int = 1,
        name: str = "مطعم النخبة",
        restaurant_type: str = "traditional",
        phone: str = "0555123456",
        wilaya: str = "الجزائر",
        lat: float = 36.75,
        lng: float = 3.06,
    ) -> dict:
        return {
            "owner_id": owner_id,
            "name": name,
            "restaurant_type": restaurant_type,
            "phone": phone,
            "wilaya": wilaya,
            "lat": lat,
            "lng": lng,
        }


class OrderFactory:
    """
    مصنع لإنشاء بيانات الطلب
    """

    @staticmethod
    def create(
        restaurant_id: int = 1,
        order_number: str = "RST1-000001",
        order_type: str = "dine_in",
        customer_name: str = "علي",
        total_amount: float = 100,
    ) -> dict:
        return {
            "restaurant_id": restaurant_id,
            "branch_id": None,
            "table_id": None,
            "employee_id": None,
            "order_number": order_number,
            "order_type": order_type,
            "customer_name": customer_name,
            "customer_phone": "0555123456",
            "delivery_address": None,
            "customer_note": None,
            "subtotal_amount": total_amount,
            "discount_amount": 0,
            "tax_amount": 0,
            "delivery_amount": 0,
            "total_amount": total_amount,
            "status": "received",
        }