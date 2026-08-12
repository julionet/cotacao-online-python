# API Spec

## Info
title: Cotação Online API
version: 1.0.0
description: API para consulta e gerenciamento de cotações financeiras
contact:
  name: Jose Julio
  email: jose.junior.229952@a.fecaf.com.br
  url: https://josejulio.com.br/suporte
license:
  name: MIT
  url: https://opensource.org/licenses/MIT
termsOfService: https://josejulio.com.br/termos

## Servers
development: http://localhost:8000
staging: https://staging.api.cotacaoonline.com.br
production: https://api.cotacaoonline.com.br

## Security
type: bearer_jwt

## Tags
- name: Auth
  description: Autenticação e gerenciamento de sessão
- name: Currency
  description: Consulta de moedas para cotação financeira
- name: Exchange
  description: Consulta de cotações financeiras
- name: Warning
  description: Consulta lista de alertas não lidos

## Schemas

### UserCreate
- name: string (required) - Nome completo do usuário
- email: string (required) - Email do usuário
- password: string (required) - Senha com mínimo de 8 caracteres

### UserResponse
- id: string (required) - UUID do usuário
- name: string (required) - Nome completo
- email: string (required) - Email do usuário
- is_active: boolean (required) - Status da conta

### LoginRequest
- email: string (required) - Email do usuário
- password: string (required) - Senha do usuário

### TokenResponse
- access_token: string (required) - Bearer token de acesso
- refresh_token: string (required) - Token para renovação
- token_type: string (required) - Tipo do token

### RefreshRequest
- refresh_token: string (required) - Token para renovação

### AccessTokenResponse
- access_token:  string (required) - Bearer token de acesso
- token_type: string (required) - Tipo do token

### CurrencyCreate
- name: string (required) - Nome da moeda
- code: string (required) - Código da moeda de origem
- codein: string (required) - Código da moeda de destino
- low: double - Valor limite inferior para alerta
- high: double - Valor limite superior para alerta

### CurrencyUpdate
- name: string (required) - Nome da moeda
- code: string (required) - Código da moeda de origem
- codein: string (required) - Código da moeda de destino
- low: double - Valor limite inferior para alerta
- high: double - Valor limite superior para alerta
- is_active: boolean (required) - Determina se moeda está ativa

### CurrencyResponse
- id: string (required) - UUID da moeda
- name: string (required) - Nome da moeda
- code: string (required) - Código da moeda de origem
- codein: string (required) - Código da moeda de destino
- low: double - Valor limite inferior para alerta
- high: double - Valor limite superior para alerta
- is_active: boolean (required) - Determina se moeda está ativa

### WarningResponse
- id: string (required) - UUID do alerta
- description: string (required) - Descrição do alerta
- timestamp: timestamp - Data e horário do alerta
- is_read: boolean (required) - Determina se alerta foi lido

### ExchangeResponse
- id: string (required) - UUID da moeda
- name: string (required) - Nome da moeda
- bid: double (required) - Valor de compra da moeda
- ask: double (required) - Valor de venda da moeda

## Endpoints

### POST /auth/register
tag: Auth
summary: Registrar novo usuário
security: none
request_body: UserCreate
responses:
  201: UserResponse
request_example:
  name: João Silva
  email: joao@exemplo.com
  password: Senh@123
response_example:
  201:
    id: 550e8400-e29b-41d4-a716-446655440000
    name: João Silva
    email: joao@exemplo.com
    is_active: true

### GET /auth/me
tag: Auth
summary: Retorna dados do usuário autenticado
security: bearer
responses:
  200: UserResponse
response_example:
  200:
    id: 550e8400-e29b-41d4-a716-446655440000
    name: João Silva
    email: joao@exemplo.com
    is_active: true

### POST /auth/login
tag: Auth
summary: Efetua autenticação do usuário
security: none
request_body: LoginRequest
  200: TokenResponse
request_example:
  email: jose@exemplo.com
  password: Senh@123
response_example:
  200:
    access_token: xxxxxx.xxxxxxxx.xxxxxxx
    refresh_token: xxxxxx.xxxxxxxx.xxxxxx
    token_type: bearer

### POST /auth/refresh
tag: Auth
summary: Efetua renovação do token de acesso
security: bearer
request_body: RefreshToken
  200: AccessTokenResponse
request_example:
  refresh_token: xxxxxx.xxxxxxxx.xxxxxxxx
response_example:
  200:
    access_token: xxxxxx.xxxxxxxx.xxxxxxx
    token_type: bearer

### POST /currencies
tag: Currency
summary: Cria uma nova moeda
security: bearer
request_body: CurrencyCreate
  201: CurrencyResponse
request_example:
  name: USD-BRL
  code: USD
  codein: BRL
  low: 2.5
  high: 5.5
response_example:
  id: 550e8400-e29b-41d4-a716-446655440000
  name: USD-BRL
  code: USD
  codein: BRL
  low: 2.5
  high: 5.5
  is_active: true

### PUT /currencies/{id}
tag: Currency
summary: Altera os dados de uma moeda
security: bearer
request_body: CurrencyUpdate
  201: CurrencyResponse
request_example:
  name: USD-BRL
  code: USD
  codein: BRL
  low: 2.5
  high: 5.5
  is_active: true
response_example:
  id: 550e8400-e29b-41d4-a716-446655440000
  name: USD-BRL
  code: USD
  codein: BRL
  low: 2.5
  high: 5.5
  is_active: true

### DELETE /currencies/{id}
tag: Currency
summary: Remove uma moeda
security: bearer
responses:
  200: 

### GET /currencies/active
tag: Currency
summary: Retorna lista de moedas ativas
security: bearer
responses:
  200: CurrencyResponse
response_example:
  200:
    id: 550e8400-e29b-41d4-a716-446655440000
    name: USD-BRL
    code: USD
    codein: BRL
    is_active: true

### GET /warnings
tag: Warning
summary: Retorna lista de alertas
security: bearer
responses:
  200: WarningResponse
response_example:
  200:
    id: 550e8400-e29b-41d4-a716-446655440000
    description: Alta da moeda USD-BRL em 10%

### GET /exchanges
tag: Exchange
summary: Retorna cotação de moedas ativas
security: bearer
response:
  200: ExchangeResponse
response_example:
  200:
    id: 550e8400-e29b-41d4-a716-446655440000
    name: USD-BRL
    bid: 4.5
    ask: 4.2

### POST /exchanges/update
tag: Exchange
summary: Atualiza cotação buscando informações em API
security: bearer
response:
  200:
