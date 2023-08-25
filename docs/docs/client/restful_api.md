---
title: restful api
#language_tabs:
#  - shell: Shell
#  - http: HTTP
#  - javascript: JavaScript
#  - ruby: Ruby
#  - python: Python
#  - php: PHP
#  - java: Java
#  - go: Go
#toc_footers: []
#includes: []
#search: true
#code_clipboard: true
#highlight_theme: darkula
#headingLevel: 2
#generator: "@tarslib/widdershins v4.0.17"
---

Base URLs: http://127.0.0.1:8080

# Default

## POST list

POST /agent/list

> Body Parameters

```json
{}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|

> Response Examples

> 200 Response

```json
{}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

## POST delete

POST /agent/delete

> Body Parameters

```json
{
  "id": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» id|body|string| yes |none|

> Response Examples

> 200 Response

```json
{}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

## POST create

POST /agent/create

> Body Parameters

```json
{
  "name": "string",
  "type": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| no |none|
|» name|body|string| yes |none|
|» type|body|string| yes |none|

> Response Examples

> 200 Response

```json
{}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

## Websocket run

Websocket /agent/run
### connect
Client send agent_id, to connect with the server.

{"id": "$AGENT_ID"}
### run
Client send user content to agent in the following format:

{"id": "$AGENT_ID", "content"： "$CONTENT"}