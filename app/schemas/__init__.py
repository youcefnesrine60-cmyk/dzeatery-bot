# ==============================================
# 📦 SCHEMAS
#  نماذج Pydantic للتحقق من البيانات.
# ==============================================

from app.schemas.restaurant import (
    RestaurantBase,
    RestaurantCreate,
    RestaurantResponse,
    RestaurantStats,
    RestaurantUpdate,
    RestaurantListResponse,      
    RestaurantData,
    RestaurantUpdateData,
    RestaurantListData,          
)

from app.schemas.owner import (
    OwnerBase,
    OwnerCreate,
    OwnerUpdate,
    OwnerStatusUpdate,      
    OwnerResponse,
    OwnerListResponse,      
    OwnerStatistics,       
    OwnerSearch,           
    TrialActivation,       
    TrialActivationResponse, 
    OwnerData,
    OwnerUpdateData,
    OwnerListData,
)

from app.schemas.registration_request import (
    RegistrationRequestBase,
    RegistrationRequestCreate,
    RegistrationRequestResponse,
    RegistrationRequestUpdate,
    RegistrationRequestStatusUpdate,
    RegistrationRequestListResponse,      
    RegistrationRequestSummary,           
    RegistrationRequestData,
    RegistrationRequestUpdateData,
    RegistrationRequestListData,          
)

from app.schemas.payment import (
    PaymentBase,
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
    PaymentStatusUpdate,
    PaymentConfirm,
    PaymentStatus,
    PaymentSummary,
    PaymentListResponse,      
    PaymentData,
    PaymentUpdateData,
    PaymentListData,          
)

from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductAvailabilityUpdate,
    ProductListResponse,
    ProductSummary,
    ProductData,
    ProductUpdateData,
)

from app.schemas.branch import (
    BranchBase,
    BranchCreate,
    BranchResponse,
    BranchUpdate,
    BranchStatusUpdate,
    BranchListResponse,
    BranchSummary,
    BranchData,
    BranchUpdateData,
)

from app.schemas.categories import (
    CategoryBase,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryListResponse,
    CategorySummary,
    CategoryData,
    CategoryUpdateData,
)

from app.schemas.order import (
    OrderBase,
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    OrderStatusUpdate,
    OrderItemCreate,
    OrderWithItemsResponse,
    OrderSummary,
    OrderData,
    OrderUpdateData,
)

from app.schemas.order_item import (
    # Order Item
    OrderItemBase,
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemResponse,
    OrderItemWithOptionsResponse,
    OrderItemListResponse,
    OrderItemSummary,
    OrderItemData,
    OrderItemUpdateData,
    OrderItemListData,
    
    # Order Item Option
    OrderItemOptionBase,
    OrderItemOptionCreate,
    OrderItemOptionUpdate,
    OrderItemOptionResponse,
    OrderItemOptionSummary,
    
    # Order Payment
    OrderPaymentBase,
    OrderPaymentCreate,
    OrderPaymentUpdate,
    OrderPaymentResponse,
    OrderPaymentStatusUpdate,
    
    # Order Status History
    OrderStatusHistoryBase,
    OrderStatusHistoryCreate,
    OrderStatusHistoryResponse,
)

from app.schemas.restaurant_payment_setting import (
    RestaurantPaymentSettingBase,
    RestaurantPaymentSettingCreate,
    RestaurantPaymentSettingResponse,
    RestaurantPaymentSettingUpdate,
    PaymentMethodsList,
    PaymentSettingsSummary,
    PaymentSettingData,
    PaymentSettingUpdateData,
)

from app.schemas.restaurant_metric import (
    RestaurantMetricBase,
    RestaurantMetricCreate,
    RestaurantMetricResponse,
    RestaurantMetricUpdate,
    RestaurantMetricSummary,
    RestaurantMetricListResponse,      
    MetricsTrendPoint,
    MetricsTrend,
    ProductMetrics,
    RestaurantMetricData,
    RestaurantMetricUpdateData,
    RestaurantMetricListData,          
)

# Restaurant Order Counter
from app.schemas.restaurant_order_counter import (
    RestaurantOrderCounterBase,
    RestaurantOrderCounterCreate,
    RestaurantOrderCounterResponse,
    RestaurantOrderCounterUpdate,
    RestaurantOrderCounterListResponse,      
    NextOrderNumberResponse,
    OrderCounterSummary,
    OrderNumberFormat,
    OrderCounterData,
    OrderCounterUpdateData,
    OrderCounterListData,                    
)

from app.schemas.option_group import (
    OptionGroupBase,
    OptionGroupCreate,
    OptionGroupResponse,
    OptionGroupUpdate,
    ProductOptionResponse,
    OptionGroupWithOptionsResponse,
    OptionGroupListResponse,      
    OptionGroupSummary,
    OptionGroupValidation,
    OptionGroupData,
    OptionGroupUpdateData,
    OptionGroupListData,
)

from app.schemas.product_option import (
    ProductOptionBase,
    ProductOptionCreate,
    ProductOptionResponse,
    ProductOptionUpdate,
    ProductOptionAvailabilityUpdate,
    ProductOptionListResponse,
    ProductOptionSummary,
    ProductOptionValidation,
    ProductOptionBulkCreate,
    ProductOptionData,
    ProductOptionUpdateData,
)

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserConsentUpdate,
    UserListResponse,
    UserSummary,
    UserSearch,
    ConsentResponse,
    UserData,
    UserUpdateData,
)

from app.schemas.admin import (
    AdminBase,
    AdminCreate,
    AdminResponse,
    AdminUpdate,
    AdminLogin,
    AdminLoginResponse,
    AdminAuthResponse,          
    AdminSessionBase,
    AdminSessionCreate,
    AdminSessionUpdate,
    AdminSessionResponse,
    AdminListResponse,
    AdminStatistics,
    AdminSearch,                
    AdminPermissionCheck,       
    AdminPermissionResponse,    
    TokenResponse,              
    RoleDistribution,
    AdminData,
    AdminUpdateData,
    AdminSessionData,
)


__all__ = [

    # Restaurant
    "RestaurantBase",
    "RestaurantCreate",
    "RestaurantResponse",
    "RestaurantStats",
    "RestaurantUpdate",
    "RestaurantListResponse",
    "RestaurantData",
    "RestaurantUpdateData",
    "RestaurantListData",

    # Owner
    "OwnerBase",
    "OwnerCreate",
    "OwnerUpdate",
    "OwnerStatusUpdate",
    "OwnerResponse",
    "OwnerListResponse",
    "OwnerStatistics",
    "OwnerSearch",
    "TrialActivation",
    "TrialActivationResponse",
    "OwnerData",
    "OwnerUpdateData",
    "OwnerListData",

    # Registration Request
    "RegistrationRequestBase",
    "RegistrationRequestCreate",
    "RegistrationRequestResponse",
    "RegistrationRequestUpdate",
    "RegistrationRequestStatusUpdate",
    "RegistrationRequestListResponse",
    "RegistrationRequestSummary",
    "RegistrationRequestData",
    "RegistrationRequestUpdateData",
    "RegistrationRequestListData",

    # Payment
    "PaymentBase",
    "PaymentCreate",
    "PaymentResponse",
    "PaymentUpdate",
    "PaymentStatusUpdate",
    "PaymentConfirm",
    "PaymentStatus",
    "PaymentSummary",
    "PaymentListResponse",
    "PaymentData",
    "PaymentUpdateData",
    "PaymentListData",

    # Product
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "ProductUpdate",
    "ProductAvailabilityUpdate",
    "ProductListResponse",
    "ProductSummary",
    "ProductData",
    "ProductUpdateData",

    # Branch
    "BranchBase",
    "BranchCreate",
    "BranchResponse",
    "BranchUpdate",
    "BranchStatusUpdate",
    "BranchListResponse",
    "BranchSummary",
    "BranchData",
    "BranchUpdateData",

    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryUpdate",
    "CategoryListResponse",
    "CategorySummary",
    "CategoryData",
    "CategoryUpdateData",

    # Order
    "OrderBase",
    "OrderCreate",
    "OrderResponse",
    "OrderUpdate",
    "OrderStatusUpdate",
    "OrderItemCreate",
    "OrderWithItemsResponse",
    "OrderSummary",
    "OrderData",
    "OrderUpdateData",

    # Order Item
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemUpdate",
    "OrderItemResponse",
    "OrderItemWithOptionsResponse",
    "OrderItemListResponse",
    "OrderItemSummary",
    "OrderItemData",
    "OrderItemUpdateData",
    "OrderItemListData",
    
    # Order Item Option
    "OrderItemOptionBase",
    "OrderItemOptionCreate",
    "OrderItemOptionUpdate",
    "OrderItemOptionResponse",
    "OrderItemOptionSummary",
    
    # Order Payment
    "OrderPaymentBase",
    "OrderPaymentCreate",
    "OrderPaymentUpdate",
    "OrderPaymentResponse",
    "OrderPaymentStatusUpdate",
    
    # Order Status History
    "OrderStatusHistoryBase",
    "OrderStatusHistoryCreate",
    "OrderStatusHistoryResponse",


    # Restaurant Payment Setting
    "RestaurantPaymentSettingBase",
    "RestaurantPaymentSettingCreate",
    "RestaurantPaymentSettingResponse",
    "RestaurantPaymentSettingUpdate",
    "PaymentMethodsList",
    "PaymentSettingsSummary",
    "PaymentSettingData",
    "PaymentSettingUpdateData",

    # Restaurant Metric
    "RestaurantMetricBase",
    "RestaurantMetricCreate",
    "RestaurantMetricResponse",
    "RestaurantMetricUpdate",
    "RestaurantMetricSummary",
    "RestaurantMetricListResponse",
    "MetricsTrendPoint",
    "MetricsTrend",
    "ProductMetrics",
    "RestaurantMetricData",
    "RestaurantMetricUpdateData",
    "RestaurantMetricListData",

    # Restaurant Order Counter
    "RestaurantOrderCounterBase",
    "RestaurantOrderCounterCreate",
    "RestaurantOrderCounterResponse",
    "RestaurantOrderCounterUpdate",
    "RestaurantOrderCounterListResponse",
    "NextOrderNumberResponse",
    "OrderCounterSummary",
    "OrderNumberFormat",
    "OrderCounterData",
    "OrderCounterUpdateData",
    "OrderCounterListData",

    # Option Group
    "OptionGroupBase",
    "OptionGroupCreate",
    "OptionGroupResponse",
    "OptionGroupUpdate",
    "ProductOptionResponse",
    "OptionGroupWithOptionsResponse",
    "OptionGroupListResponse",
    "OptionGroupSummary",
    "OptionGroupValidation",
    "OptionGroupData",
    "OptionGroupUpdateData",
    "OptionGroupListData",

    # Product Option
    "ProductOptionBase",
    "ProductOptionCreate",
    "ProductOptionResponse",
    "ProductOptionUpdate",
    "ProductOptionAvailabilityUpdate",
    "ProductOptionListResponse",
    "ProductOptionSummary",
    "ProductOptionValidation",
    "ProductOptionBulkCreate",
    "ProductOptionData",
    "ProductOptionUpdateData",

    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserConsentUpdate",
    "UserListResponse",
    "UserSummary",
    "UserSearch",
    "ConsentResponse",
    "UserData",
    "UserUpdateData",

    # Admin
    "AdminBase",
    "AdminCreate",
    "AdminResponse",
    "AdminUpdate",
    "AdminLogin",
    "AdminLoginResponse",
    "AdminAuthResponse",
    "AdminSessionBase",
    "AdminSessionCreate",
    "AdminSessionUpdate",
    "AdminSessionResponse",
    "AdminListResponse",
    "AdminStatistics",
    "AdminSearch",
    "AdminPermissionCheck",
    "AdminPermissionResponse",
    "TokenResponse",
    "RoleDistribution",
    "AdminData",
    "AdminUpdateData",
    "AdminSessionData",

]