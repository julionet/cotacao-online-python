# Referência: Mapeamento de Tipos

## Tipos primitivos

| Tipo no SPEC.md | OpenAPI type / format              |
|------------------|-------------------------------------|
| `string`         | `type: string`                      |
| `int`            | `type: integer`                     |
| `float`          | `type: number` / `format: float`    |
| `double`         | `type: number` / `format: double`   |
| `bool`/`boolean` | `type: boolean`                     |
| `uuid`           | `type: string` / `format: uuid`     |
| `date`           | `type: string` / `format: date`     |
| `datetime`       | `type: string` / `format: date-time`|
| `email`          | `type: string` / `format: email`    |

## Modificadores → YAML (OpenAPI 3.1 / JSON Schema)

> **Atenção — nullable em 3.1:** OpenAPI 3.1 usa JSON Schema 2020-12. O `nullable: true` do 3.0 **não existe** em 3.1 e não deve ser gerado. Um campo nullable é representado com `type` como array incluindo `"null"`.

| Modificador no SPEC.md | Geração em YAML |
|---|---|
| `nullable` | `type: [{tipo mapeado}, "null"]` no lugar de `type: {tipo mapeado}` |
| `enum: v1,v2,v3` | `enum: [v1, v2, v3]` |
| `default: valor` | `default: {valor}` |
| `minLength: n` | `minLength: {n}` (apenas em campos `string`) |
| `maxLength: n` | `maxLength: {n}` (apenas em campos `string`) |
| `pattern: regex` | `pattern: '{regex}'` (apenas em campos `string`) |
| `minimum: n` | `minimum: {n}` (apenas em campos `int`/`float`/`double`) |
| `maximum: n` | `maximum: {n}` (apenas em campos `int`/`float`/`double`) |

**Exemplo combinando tipo + modificadores:**

SPEC.md:
```
- role: string (optional) [enum: user,admin, default: user] - Papel do usuário
- deleted_at: datetime (optional) [nullable] - Data de exclusão lógica
- age: int (optional) [nullable, minimum: 0, maximum: 150] - Idade do usuário
```

YAML gerado:
```yaml
role:
  type: string
  enum: [user, admin]
  default: user
  description: Papel do usuário
deleted_at:
  type: [string, "null"]
  format: date-time
  description: Data de exclusão lógica
age:
  type: [integer, "null"]
  minimum: 0
  maximum: 150
  description: Idade do usuário
```

Regra de ordenação dentro do bloco de propriedade: `type` (ou `type` + `format`), depois `enum`, depois `default`, depois constraints (`minLength`/`maxLength`/`pattern`/`minimum`/`maximum`), depois `description` por último.
