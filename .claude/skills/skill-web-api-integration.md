# Skill: Integrar Endpoint de API com React Query

Você é responsável por integrar um endpoint de API REST a um projeto React + TypeScript existente, usando TanStack Query (React Query) para gerenciar cache, loading e estados de erro.

## Como Invocar

O usuário deve fornecer:

**Para buscar dados (GET):**
```
endpoint: GET /v1/{recurso}
entidade: {NomeDaEntidade}
descrição: {o que este endpoint retorna}
request: {parâmetros de query ou path, se houver}
response: {campos do objeto retornado}
```

**Para enviar/modificar dados (POST/PUT/DELETE):**
```
endpoint: {METHOD} /v1/{recurso}
entidade: {NomeDaEntidade}
descrição: {o que este endpoint faz}
request: {campos do body}
response: {campos do objeto retornado ou "void"}
```

---

## O Que Esta Skill Faz

Para cada integração, gera ou atualiza:

1. **Tipos TypeScript** em `src/types/index.ts` — interfaces para request e response
2. **Função de serviço** em `src/services/{entidade}Service.ts` — chamada Axios tipada
3. **Hook React Query** em `src/hooks/use{Entidade}s.ts` — `useQuery` para GET, `useMutation` para POST/PUT/DELETE

---

## Estrutura Gerada

### `src/types/index.ts` — adicionar ao arquivo existente

```typescript
// Tipos da entidade {NomeDaEntidade}
export interface {NomeDaEntidade} {
  id: string
  // demais campos conforme response do endpoint
}

export interface {NomeDaEntidade}Request {
  // campos do body conforme request do endpoint
}

// Para listagens paginadas (quando o endpoint retornar paginação):
export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
```

### `src/services/{entidade}Service.ts`

```typescript
import api from './api'
import type { {NomeDaEntidade}, {NomeDaEntidade}Request } from '@/types'

export const {entidade}Service = {
  getAll: async (): Promise<{NomeDaEntidade}[]> => {
    const response = await api.get<{NomeDaEntidade}[]>('/v1/{recurso}')
    return response.data
  },

  getById: async (id: string): Promise<{NomeDaEntidade}> => {
    const response = await api.get<{NomeDaEntidade}>(`/v1/{recurso}/${id}`)
    return response.data
  },

  create: async (data: {NomeDaEntidade}Request): Promise<{NomeDaEntidade}> => {
    const response = await api.post<{NomeDaEntidade}>('/v1/{recurso}', data)
    return response.data
  },

  update: async (id: string, data: Partial<{NomeDaEntidade}Request>): Promise<{NomeDaEntidade}> => {
    const response = await api.put<{NomeDaEntidade}>(`/v1/{recurso}/${id}`, data)
    return response.data
  },

  remove: async (id: string): Promise<void> => {
    await api.delete(`/v1/{recurso}/${id}`)
  },
}
```

Gere apenas as funções correspondentes aos endpoints informados — não crie funções para endpoints que não existem.

---

## Hooks React Query

### Hook para GET (buscar lista)

**`src/hooks/use{Entidade}s.ts`**

```typescript
import { useQuery } from '@tanstack/react-query'
import { {entidade}Service } from '@/services/{entidade}Service'

export function use{Entidade}s() {
  return useQuery({
    queryKey: ['{recurso}'],
    queryFn: {entidade}Service.getAll,
  })
}
```

### Hook para GET (buscar por ID)

```typescript
import { useQuery } from '@tanstack/react-query'
import { {entidade}Service } from '@/services/{entidade}Service'

export function use{Entidade}(id: string) {
  return useQuery({
    queryKey: ['{recurso}', id],
    queryFn: () => {entidade}Service.getById(id),
    enabled: !!id,
  })
}
```

### Hook para GET com parâmetros de query (filtros/paginação)

```typescript
import { useQuery } from '@tanstack/react-query'
import { {entidade}Service } from '@/services/{entidade}Service'

interface Query{Entidade}sParams {
  page?: number
  size?: number
  search?: string
}

export function use{Entidade}s(params: Query{Entidade}sParams = {}) {
  return useQuery({
    queryKey: ['{recurso}', params],
    queryFn: () => {entidade}Service.getAll(params),
  })
}
```

### Hook para POST (criar)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { {entidade}Service } from '@/services/{entidade}Service'
import type { {NomeDaEntidade}Request } from '@/types'

export function useCreate{Entidade}() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: {NomeDaEntidade}Request) => {entidade}Service.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['{recurso}'] })
      toast.success('{NomeDaEntidade} criado com sucesso!')
    },
    onError: () => {
      toast.error('Erro ao criar {NomeDaEntidade}. Tente novamente.')
    },
  })
}
```

### Hook para PUT (atualizar)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { {entidade}Service } from '@/services/{entidade}Service'
import type { {NomeDaEntidade}Request } from '@/types'

export function useUpdate{Entidade}() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<{NomeDaEntidade}Request> }) =>
      {entidade}Service.update(id, data),
    onSuccess: (_result, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['{recurso}'] })
      queryClient.invalidateQueries({ queryKey: ['{recurso}', id] })
      toast.success('{NomeDaEntidade} atualizado com sucesso!')
    },
    onError: () => {
      toast.error('Erro ao atualizar {NomeDaEntidade}. Tente novamente.')
    },
  })
}
```

### Hook para DELETE (remover)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { {entidade}Service } from '@/services/{entidade}Service'

export function useDelete{Entidade}() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => {entidade}Service.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['{recurso}'] })
      toast.success('{NomeDaEntidade} removido com sucesso!')
    },
    onError: () => {
      toast.error('Erro ao remover {NomeDaEntidade}. Tente novamente.')
    },
  })
}
```

---

## Como Usar os Hooks nas Páginas

### Exemplo — listar com loading e erro

```tsx
import { use{Entidade}s } from '@/hooks/use{Entidade}s'
import { Skeleton } from '@/components/ui/skeleton'

export default function {Entidade}ListPage() {
  const { data: items, isLoading, isError } = use{Entidade}s()

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    )
  }

  if (isError) {
    return <p className="text-destructive">Erro ao carregar dados. Tente novamente.</p>
  }

  return (
    <ul className="space-y-2">
      {items?.map((item) => (
        <li key={item.id}>{/* renderizar item */}</li>
      ))}
    </ul>
  )
}
```

### Exemplo — criar com formulário e mutation

```tsx
import { useCreate{Entidade} } from '@/hooks/use{Entidade}s'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const schema = z.object({
  // campos conforme {NomeDaEntidade}Request
})

type FormData = z.infer<typeof schema>

export default function Create{Entidade}Form() {
  const { mutate, isPending } = useCreate{Entidade}()
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = (data: FormData) => {
    mutate(data, { onSuccess: () => reset() })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* campos do formulário */}
      <Button type="submit" disabled={isPending}>
        {isPending ? 'Salvando...' : 'Salvar'}
      </Button>
    </form>
  )
}
```

---

## Adicionando ao Service de API (quando não existe serviço separado)

Se o endpoint for simples e não justificar um arquivo de serviço separado, adicione a função diretamente no arquivo de serviço relevante ou use `api` diretamente na mutation:

```typescript
// Uso direto do api no hook, para endpoints simples
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import api from '@/services/api'
import type { AlgumRequest } from '@/types'

export function useAlgumaAcao() {
  return useMutation({
    mutationFn: (data: AlgumRequest) => api.post('/v1/alguma-rota', data).then((r) => r.data),
    onSuccess: () => toast.success('Ação concluída!'),
    onError: () => toast.error('Erro ao executar ação.'),
  })
}
```

---

## Regras de Execução

1. **Gere apenas** os hooks e funções correspondentes aos endpoints informados — não invente endpoints
2. **Sempre invalide** o queryKey após mutations (`invalidateQueries`) para manter o cache atualizado
3. **`enabled: !!id`** em queries que dependem de um parâmetro opcional — evita chamada com valor vazio
4. **Nunca repita tipos** já definidos em `src/types/index.ts` — adicione apenas os novos
5. **Crie o arquivo de serviço** em `src/services/` somente se não existir ainda; se já existir, adicione as novas funções ao final
6. **Crie a pasta `src/hooks/`** se não existir
7. Ao final, liste os arquivos criados e os arquivos modificados separadamente
