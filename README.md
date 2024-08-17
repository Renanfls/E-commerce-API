# Documentação da API de E-commerce em Flask

## Visão Geral

Este documento descreve os endpoints da API para uma aplicação de e-commerce baseada em Flask. A API lida com autenticação de usuários, gerenciamento de produtos e funcionalidades de carrinho de compras.

## Autenticação

### Login

```jsx
POST /login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Logout

```jsx
POST /logout
Authorization: Bearer {token}
```

## Gerenciamento de Produtos

### Adicionar Produto

```jsx
POST /api/products/add
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "string",
  "price": float,
  "description": "string"
}
```

### Excluir Produto

```jsx
DELETE /api/products/delete/{product_id}
Authorization: Bearer {token}
```

### Obter Detalhes do Produto

```jsx
GET /api/products/{product_id}
```

### Atualizar Produto

```jsx
PUT /api/products/update/{product_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "string",
  "price": float,
  "description": "string"
}
```

### Obter Todos os Produtos

```jsx
GET /api/products
```

## Carrinho de Compras

### Adicionar ao Carrinho

```jsx
POST /api/cart/add/{product_id}
Authorization: Bearer {token}
```

### Remover do Carrinho

```jsx
DELETE /api/cart/remove/{product_id}
Authorization: Bearer {token}
```

### Visualizar Carrinho

```jsx
GET /api/cart
Authorization: Bearer {token}
```

### Finalizar Compra

```jsx
POST /api/cart/checkout
Authorization: Bearer {token}
```

## Modelos

### Usuário

- id: Inteiro (Chave Primária)
- username: String (Único, Não Nulo)
- password: String
- cart: Relacionamento com CartItem

### Produto

- id: Inteiro (Chave Primária)
- name: String (Não Nulo)
- price: Float (Não Nulo)
- description: Texto

### Item do Carrinho

- id: Inteiro (Chave Primária)
- user_id: Inteiro (Chave Estrangeira para Usuário)
- product_id: Inteiro (Chave Estrangeira para Produto)

## Segurança

A API utiliza Flask-Login para autenticação de usuários. A maioria dos endpoints requer que o usuário esteja logado, o que é garantido pelo decorador @login_required.

## Banco de Dados

A aplicação usa SQLAlchemy como ORM com um banco de dados especificado pela variável de ambiente DATABASE_URL.

## Executando a Aplicação

Para executar a aplicação, certifique-se de que todas as dependências estejam instaladas e as variáveis de ambiente estejam configuradas. Em seguida, execute o script com Python.

```Shell
pip3 install -r requirements.txt
```
