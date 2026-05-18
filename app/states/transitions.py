from app.states.owner_states import OwnerStates


ALLOWED_TRANSITIONS = {

    OwnerStates.NAME: [

        OwnerStates.RESTAURANT_NAME
    ],

    OwnerStates.RESTAURANT_NAME: [

        OwnerStates.WILAYA
    ],

    OwnerStates.WILAYA: [

        OwnerStates.LOCATION
    ],

    OwnerStates.LOCATION: [

        OwnerStates.TYPE
    ],

    OwnerStates.TYPE: [

        OwnerStates.PHONE
    ],

    OwnerStates.PHONE: [

        OwnerStates.CONFIRM
    ]
}