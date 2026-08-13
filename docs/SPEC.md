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

### CurrencyResponse
- id: string (required) - Identificação da moeda
- name: string (required) - Nome da moeda
- code: string (required) - Código da moeda de origem
- codein: string (required) - Código da moeda de destino
- last_date: datetime (required) - Data e hora da última atualização

### ExchangeResponse
- name: string (required) - Nome da moeda
- bid: float (required) - Valor de compra da moeda
- ask: float (required) - Valor de venda da moeda

## Endpoints

### POST /v1/auth/register
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

### GET /v1/auth/me
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

### POST /v1/auth/login
tag: Auth
summary: Efetua autenticação do usuário
security: none
request_body: LoginRequest
responses:
  200: TokenResponse
request_example:
  email: jose@exemplo.com
  password: Senh@123
response_example:
  200:
    access_token: xxxxxx.xxxxxxxx.xxxxxxx
    refresh_token: xxxxxx.xxxxxxxx.xxxxxx
    token_type: bearer

### POST /v1/auth/refresh
tag: Auth
summary: Efetua renovação do token de acesso
security: bearer
request_body: RefreshRequest
responses:
  200: AccessTokenResponse
request_example:
  refresh_token: xxxxxx.xxxxxxxx.xxxxxxxx
response_example:
  200:
    access_token: xxxxxx.xxxxxxxx.xxxxxxx
    token_type: bearer

### GET /v1/currencies
tag: Currency
summary: Retorna lista de moedas ativas
security: bearer
responses:
  200: list[CurrencyResponse]
response_example:
  200:
    id: recFTu2BE9PnKgJ4u
    name: USD-BRL
    code: USD
    codein: BRL
    last_date: 2026-08-12T20:00:00

### GET /v1/exchanges
tag: Exchange
summary: Retorna lista de cotações de moedas
security: bearer
responses:
  200: list[ExchangeResponse]
response_example:
  200:
    name: USD-BRL
    bid: 4.5
    ask: 4.2

### POST /v1/exchanges/sync
tag: Exchange
summary: Atualiza cotação buscando informações em API
security: bearer
responses:
  200: (sem corpo de resposta)
