# eWallet Micro Service
##### Closed eWallet Service

### Installation

1. Clone the repository:
``` https://github.com/DotOp3rator011/eWalletMicroService.git ```

2. Install requirements:
``` pip insatll -r requirements.txt ```

### Data Flow Diagram
![](images/dfd.png?raw=true)

### Schema Design
![](images/schemadesign.png?raw=true)

### API documention

##### The documentaion can be viewed using the following endpoint
``` /wallet/docs/ ```

#### Documnetation snippet from swagger
```yaml
swagger: '2.0'
info:
  version: 0.0.0
  title: wallet
  description: API for wallet micro service
host: 'localhost:8080'
basePath: /wallet
schemes:
  - https
paths:
  /update_currencies:
    put:
      summary: Updates currencies
      description: Update currencies through the currency config file
      parameters:
        - in: body
          name: update_currencies
          schema:
            $ref: '#/definitions/CurrencyForceUpdate'
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/UpdateCurrency'
  /allowed_currencies:
    get:
      summary: Returns allowed currencies
      description: Returns a list of allowed currencies
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Currencies'
  /create_wallet:
    post:
      summary: Create user wallet
      description: >-
        Create a wallet for the user for specified currency and return the
        wallet Id
      parameters:
        - in: body
          name: create_wallet
          schema:
            $ref: '#/definitions/CreateWallet'
      responses:
        '201':
          description: CREATED
          schema:
            $ref: '#/definitions/WalletId'
  /credit:
    put:
      summary: Credit to user wallet
      description: Credit the specified amount in the user's wallet
      parameters:
        - in: body
          name: credit
          schema:
            $ref: '#/definitions/UpdateWallet'
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Balance'
  /debit:
    put:
      summary: Debit from user wallet
      description: Debit the specified amount from thr user's wallet
      parameters:
        - in: body
          name: debit
          schema:
            $ref: '#/definitions/UpdateWallet'
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Balance'
  /transactions:
    post:
      summary: Returns transactions
      description: Returns list of all or filtered transactions in detail
      parameters:
        - in: body
          name: filters
          description: filters necessary to filter the transactions
          schema:
            $ref: '#/definitions/Filters'
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Transactions'
  /user/wallets:
    get:
      summary: Returns current user's wallets
      description: Returns the list  of wallets owned by the current user
      parameters:
        - in: query
          name: user_id
          description: The Id of the current user
          type: string
          required: true
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/UserWallets'
  /user/balance:
    get:
      summary: Retruns balance amount is user's wallet
      description: Returns the balance amount in the current user's specified wallet
      parameters:
        - in: query
          name: user_id
          description: The Id of the current user's desired wallet
          required: true
          type: string
        - in: query
          name: currenncy
          description: The currency of the wallet
          required: true
          type: string
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Balance'
  /activate:
    put:
      summary: activate a wallet
      description: activates a deactivated wallet
      parameters:
        - in: body
          name: activate
          schema:
            $ref: '#/definitions/UserWallet'
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/WalletStatusMessage'
  /deactivate:
    put:
      summary: deactivate a wallet
      description: deactivates an active wallet
      parameters:
        - in: body
          name: deactivate
          schema:
            $ref: '#/definitions/UserWallet'
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/WalletStatusMessage'
definitions:
  CreateWallet:
    type: object
    required:
      - user_id currency
    properties:
      user_id:
        type: string
      currency:
        type: string
  WalletId:
    type: object
    properties:
      wallet_id:
        type: string
      message:
        type: string
      request_status:
        type: number
  UpdateWallet:
    type: object
    required:
      - user_id
      - currency
      - amount
    properties:
      user_id:
        type: string
      currency:
        type: string
      amount:
        type: number
      source:
        type: string
      payment_id:
        type: string
      Transaction_remarks:
        type: string
  Balance:
    type: object
    properties:
      current_balance:
        type: number
      message:
        type: string
      request_status:
        type: number
  UserWallets:
    type: object
    properties:
      wallets:
        type: array
        items:
          type: object
          properties:
            wallet_id:
              type: string
            balance:
              type: number
      message:
        type: string
      request_status:
        type: number
  Filters:
    type: object
    properties:
      user_id:
        type: string
      transaction_type:
        type: string
      start_date:
        type: string
      end_date:
        type: string
  Transactions:
    type: object
    properties:
      transactions:
        type: array
        items:
          type: object
          properties:
            transaction_id:
              type: string
            payment_id:
              type: string
            source:
              type: string
            transaction_date:
              type: string
            transaction_time:
              type: string
            previous_balance:
              type: number
            transaction_amount:
              type: number
            current_balance:
              type: number
            transaction_remarks:
              type: string
            wallet_id:
              type: string
            transaction_type:
              type: string
      message:
        type: string
      request_status:
        type: number
  Currencies:
    type: object
    properties:
      currency_list:
        type: array
        items:
          type: object
          properties:
            currency_name:
              type: string
            limit:
              type: number
      request_status:
        type: number
  UserWallet:
    type: object
    required:
      - user_id currency
    properties:
      user_id:
        type: string
      currency:
        type: string
  WalletStatusMessage:
    type: object
    properties:
      message:
        type: string
      request_status:
        type: number
  CurrencyForceUpdate:
    type: object
    properties:
      limit_hard:
        type: boolean
      status_hard:
        type: boolean
  UpdateCurrency:
    type: object
    properties:
      currency_status:
        type: object
        properties:
          user:
            type: array
            items:
              type: object
              properties:
                currency_id:
                  type: number
                user_id:
                  type: string
                current_balance:
                  type: number
                active:
                  type: boolean
          message:
            type: string
          request_status:
            type: number
      currency_limit:
        type: object
        properties:
          user:
            type: array
            items:
              type: object
              properties:
                currency_id:
                  type: number
                user_id:
                  type: string
                current_balance:
                  type: number
                active:
                  type: boolean
          message:
            type: string
          request_status:
            type: number
      message:
        type: string
      request_status:
        type: number
```