# Guia de Autenticação Manual via Pipeboard API

Este guia documenta como autenticar manualmente com a API do Pipeboard para usar o Meta Ads MCP.

## Pré-requisitos

1. Pipeboard rodando localmente em `http://pipeboard.localhost:4000`
2. API Token do Pipeboard (obtenha em [pipeboard.localhost:4000/api-tokens](http://pipeboard.localhost:4000/api-tokens))
3. Servidor MCP rodando localmente

## Configuração do Ambiente Local

Antes de iniciar, abra no navegador:

```
http://pipeboard.localhost:4000
```

Faça login e obtenha seu API Token em **API Tokens**.

## Iniciar o Servidor MCP

```powershell
$env:PIPEBOARD_API_TOKEN = "pk_seu_token_aqui"

uv run python -m meta_ads_mcp --transport streamable-http --port 9001
```

## Endpoints da API Pipeboard

| Endpoint | Método | Quando usar |
|----------|--------|-------------|
| `/meta/auth` | POST | Iniciar novo login (retorna URL do browser) |
| `/meta/token` | GET | Obter access token (quando já autenticado) |

## Fluxo de Autenticação

### Passo 1: Definir o API Token

```powershell
$API_TOKEN = "pk_seu_token_aqui"
```

### Passo 2: Verificar se já está autenticado

Tente obter o access token diretamente:

```powershell
$response = Invoke-WebRequest `
  -Uri "https://pipeboard.co/api/meta/token?api_token=$API_TOKEN" `
  -Method GET

$response.Content
```

**Se retornar status 200 com `access_token`**: Você já está autenticado! Pule para o Passo 5.

**Se retornar erro 404**: Você precisa fazer login. Continue com o Passo 3.

### Passo 3: Iniciar Login (apenas se necessário)

```powershell
$authResponse = Invoke-WebRequest `
  -Uri "https://pipeboard.co/api/meta/auth?api_token=$API_TOKEN" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" }

# Extrair e abrir URL de login
$loginUrl = ($authResponse.Content | ConvertFrom-Json).loginUrl
Start-Process $loginUrl
```

### Passo 4: Autorizar no Browser

1. O browser vai abrir automaticamente
2. Faça login na sua conta Meta/Facebook
3. Autorize o acesso ao aplicativo

### Passo 5: Obter o Access Token

```powershell
$tokenResponse = Invoke-WebRequest `
  -Uri "https://pipeboard.co/api/meta/token?api_token=$API_TOKEN" `
  -Method GET

$accessToken = ($tokenResponse.Content | ConvertFrom-Json).access_token
Write-Host "Access Token: $accessToken"
```

### Passo 6: Fazer chamadas ao Servidor MCP

#### Listar ferramentas disponíveis:

```powershell
Invoke-WebRequest `
  -Uri "http://localhost:9001/mcp" `
  -Method POST `
  -Headers @{ 
    "Content-Type" = "application/json"
    "Accept" = "application/json, text/event-stream"
    "Authorization" = "Bearer $accessToken"
  } `
  -Body '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

#### Listar Ad Accounts:

```powershell
$body = @{
  jsonrpc = "2.0"
  method = "tools/call"
  id = 1
  params = @{
    name = "get_ad_accounts"
    arguments = @{ limit = 5 }
  }
} | ConvertTo-Json -Depth 5

Invoke-WebRequest `
  -Uri "http://localhost:9001/mcp" `
  -Method POST `
  -Headers @{ 
    "Content-Type" = "application/json"
    "Accept" = "application/json, text/event-stream"
    "Authorization" = "Bearer $accessToken"
  } `
  -Body $body
```

#### Obter Insights de uma Conta:

```powershell
$body = @{
  jsonrpc = "2.0"
  method = "tools/call"
  id = 1
  params = @{
    name = "get_insights"
    arguments = @{
      object_id = "act_SEU_ACCOUNT_ID"
      time_range = "last_30d"
      level = "campaign"
    }
  }
} | ConvertTo-Json -Depth 5

Invoke-WebRequest `
  -Uri "http://localhost:9001/mcp" `
  -Method POST `
  -Headers @{ 
    "Content-Type" = "application/json"
    "Accept" = "application/json, text/event-stream"
    "Authorization" = "Bearer $accessToken"
  } `
  -Body $body
```

## Script Completo

Aqui está um script PowerShell completo para autenticação e teste:

```powershell
# Configuração
$API_TOKEN = "pk_seu_token_aqui"
$MCP_URL = "http://localhost:9001/mcp"

# 1. Obter Access Token
Write-Host "Obtendo access token do Pipeboard..."
$tokenResponse = Invoke-WebRequest `
  -Uri "https://pipeboard.co/api/meta/token?api_token=$API_TOKEN" `
  -Method GET

$accessToken = ($tokenResponse.Content | ConvertFrom-Json).access_token
Write-Host "✅ Access token obtido!"

# 2. Configurar headers
$headers = @{ 
  "Content-Type" = "application/json"
  "Accept" = "application/json, text/event-stream"
  "Authorization" = "Bearer $accessToken"
}

# 3. Listar Ad Accounts
Write-Host "Listando Ad Accounts..."
$body = @{
  jsonrpc = "2.0"
  method = "tools/call"
  id = 1
  params = @{
    name = "get_ad_accounts"
    arguments = @{ limit = 5 }
  }
} | ConvertTo-Json -Depth 5

$response = Invoke-WebRequest -Uri $MCP_URL -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## Troubleshooting

### Erro 401 no `/meta/auth`

Se você receber erro 401 ao chamar `/meta/auth`, pode significar:

1. **Já está autenticado**: Tente `/meta/token` em vez de `/meta/auth`
2. **Token inválido**: Verifique se o API token está correto
3. **Token expirado**: Gere um novo token em [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)

### Erro 401 no `/meta/token`

- O API token do Pipeboard está inválido ou expirado
- Gere um novo token no Pipeboard

### Erro de conexão no servidor MCP

- Verifique se o servidor está rodando: `uv run python -m meta_ads_mcp --transport streamable-http --port 9001`
- Verifique se a porta está correta (9001)

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `PIPEBOARD_API_TOKEN` | Token da API do Pipeboard |
| `META_ACCESS_TOKEN` | Token de acesso direto do Meta (alternativa) |
| `META_APP_ID` | ID do App Meta (para OAuth próprio) |

## Referências

- [Pipeboard.co](https://pipeboard.co)
- [Meta Graph API](https://developers.facebook.com/docs/graph-api/)
- [Streamable HTTP Setup Guide](STREAMABLE_HTTP_SETUP.md)

