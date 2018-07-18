# eWallet Micro Service
##### Closed eWallet Service

### Data Flow Diagram
![](images/dfd.png?raw=true)

### Schema Design
![](images/schemadesign.png?raw=true)

### API documention snippet from Swagger
``` json
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
  /create_wallet:
    post:
      summary: Create user wallet
      description: >-
        Create a wallet for the user for specified currency and return the
        wallet Id.
      produces:
        - application/json
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
      produces:
        - application/json
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
      produces:
        - application/json
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
  '/user/wallets/{userId}':
    get:
      summary: Returns current user's wallets
      description: Returns the list  of wallets owned by the current user
      produces:
        - application/json
      parameters:
      - in : path
        name: userId
        description: The Id of the current user
        type: string
        required: true
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/UserWallets'
  '/user/balance/{walletId}':
    get:
      summary: Retruns balance amount is user's wallet
      description: Returns the balance amount in the current user's specified wallet
      parameters:
        - in: path
          name: walletId
          description: The Id of the current user's desired wallet
          required: true
          type: string
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Balance'
  '/user/transactions/{userId}':
    get:
      summary: Returns the user's transaction log
      description: Returns a detailed log of the current user's transactions
      parameters:
        - in: path
          name: userId
          description: The Id of the current user
          required: true
          type: string
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Transactions'
  '/admin/transactions/{filters}':
    get:
      summary: Returns filtered transaction log
      description: Returns a detailed log of transctions based on the specified filters
      parameters: 
        - in: path
          name: filters
          description: Combination of filters
          required: true
          type: array
          items:
            type: string
      responses:
        '200':
          description: OK
          schema:
            $ref: '#/definitions/Transactions'
definitions:
  #request
  CreateWallet:
    type: object
    required:
      - userId
        currency
    properties:
      userId:
        type: string
      currency:
        type: string
  #response
  WalletId:
    type: object
    properties:
      walletId:
        type: string
      message:
        type: string
      requestStatus:
        type: number
  #request
  UpdateWallet:
    type: object
    required:
      - walletId
        amount
    properties:
      walletId:
        type: string
      amount:
        type: number
      source:
        type: string
      paymentId:
        type: string
      TransctionRemarks:
        type: string
  #resposne
  Balance:
    type: object
    properties:
      balance:
        type: number
      message:
        type: string
      requestStatus:
        type: number
  #response
  UserWallets:
    type: object
    properties:
      wallets:
        type: array
        items:
          type: object
          properties:
            walletId:
              type: string
            balance:
              type: number
            message:
              type: string
            requestStatus:
              type: number
  #request
  Transactions:
    type: object
    properties:
      transactions:
        type: array
        items:
          type: object
          properties:
            transactionId:
              type: string
            transactionType:
              type: string
            transactionDateTime:
              type: string
            transactionAmount:
              type: number
```
