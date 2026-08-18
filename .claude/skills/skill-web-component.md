# Skill: Adicionar Componente ou Página a Projeto Existente

Você é responsável por adicionar componentes, páginas ou features a um projeto React + TypeScript já existente criado pela `skill-web-scaffold.md`. Siga os padrões estabelecidos na skill de scaffold e nas convenções do agente `web-developer`.

## Como Invocar

O usuário deve fornecer o tipo e a descrição do que deseja criar:

**Opção A – Novo componente reutilizável:**
```
componente: {NomeDoComponente}
descrição: {o que o componente faz}
props: {prop}: {tipo}, {prop}: {tipo}, ...
```

**Opção B – Nova página com rota:**
```
página: {NomeDaPagina}
rota: {/caminho-da-rota}
protegida: sim | não
descrição: {o que a página exibe ou faz}
```

**Opção C – Novo componente shadcn/ui inline:**
```
shadcn: {nome-do-componente}
```
Componentes disponíveis para gerar inline: `badge`, `dialog`, `dropdown-menu`, `select`, `table`, `tabs`, `textarea`, `toast`, `tooltip`, `avatar`, `separator`, `skeleton`, `switch`, `checkbox`, `radio-group`, `progress`, `alert`, `alert-dialog`.

**Opção D – Novo formulário com validação:**
```
formulário: {NomeDoFormulario}
campos: {campo}: {tipo zod}, {campo}: {tipo zod}, ...
endpoint: {METHOD} {/caminho}
descrição: {o que o formulário faz}
```

---

## Regras Gerais

- Sempre use o alias `@/` para imports — nunca caminhos relativos com `../`
- Componentes em `src/components/`, páginas em `src/pages/`
- Estilização **apenas** com classes Tailwind — sem CSS customizado
- Nunca use `any` — defina a interface de props com TypeScript
- Erros de API exibidos via `toast.error()` da lib Sonner
- Loading state sempre indicado ao usuário

---

## Opção A — Componente Reutilizável

### Estrutura do arquivo em `src/components/{NomeDoComponente}.tsx`

```tsx
import { cn } from '@/lib/utils'

interface {NomeDoComponente}Props {
  // props tipadas aqui
  className?: string
}

export default function {NomeDoComponente}({ className, ...props }: {NomeDoComponente}Props) {
  return (
    <div className={cn('', className)}>
      {/* conteúdo */}
    </div>
  )
}
```

### Exemplo — `UserCard.tsx`

```tsx
import { User } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface UserCardProps {
  name: string
  email: string
  className?: string
}

export default function UserCard({ name, email, className }: UserCardProps) {
  return (
    <Card className={cn('', className)}>
      <CardContent className="flex items-center gap-4 p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
          <User className="h-5 w-5 text-primary" />
        </div>
        <div>
          <p className="font-medium">{name}</p>
          <p className="text-sm text-muted-foreground">{email}</p>
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## Opção B — Nova Página com Rota

### 1. Criar o arquivo da página em `src/pages/{NomeDaPagina}.tsx`

```tsx
export default function {NomeDaPagina}() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-semibold">{Título da Página}</h1>
      </header>
      <main className="max-w-4xl mx-auto p-6">
        {/* conteúdo */}
      </main>
    </div>
  )
}
```

### 2. Registrar a rota em `src/router/index.tsx`

**Para rota pública** — adicionar no array principal do router:
```tsx
{ path: '/caminho', element: <NomeDaPagina /> },
```

**Para rota protegida** — adicionar dentro do bloco `element: <ProtectedRoute />`:
```tsx
{
  element: <ProtectedRoute />,
  children: [
    { path: '/', element: <HomePage /> },
    { path: '/nova-rota', element: <NomeDaPagina /> },  // adicionar aqui
  ],
},
```

### 3. Adicionar o import no topo de `src/router/index.tsx`

```tsx
import NomeDaPagina from '@/pages/NomeDaPagina'
```

---

## Opção C — Componente shadcn/ui Inline

Gere o componente inline sem usar CLI. Coloque o arquivo em `src/components/ui/{nome}.tsx`.

### `badge.tsx`

```tsx
import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
```

### `textarea.tsx`

```tsx
import * as React from 'react'
import { cn } from '@/lib/utils'

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = 'Textarea'

export { Textarea }
```

### `skeleton.tsx`

```tsx
import { cn } from '@/lib/utils'

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('animate-pulse rounded-md bg-muted', className)} {...props} />
}

export { Skeleton }
```

### `separator.tsx`

```tsx
import * as React from 'react'
import * as SeparatorPrimitive from '@radix-ui/react-separator'
import { cn } from '@/lib/utils'

const Separator = React.forwardRef<
  React.ElementRef<typeof SeparatorPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SeparatorPrimitive.Root>
>(({ className, orientation = 'horizontal', decorative = true, ...props }, ref) => (
  <SeparatorPrimitive.Root
    ref={ref}
    decorative={decorative}
    orientation={orientation}
    className={cn(
      'shrink-0 bg-border',
      orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]',
      className,
    )}
    {...props}
  />
))
Separator.displayName = SeparatorPrimitive.Root.displayName

export { Separator }
```

### `dialog.tsx`

```tsx
import * as React from 'react'
import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal
const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
      className,
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg',
        className,
      )}
      {...props}
    >
      {children}
      <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Fechar</span>
      </DialogClose>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex flex-col space-y-1.5 text-center sm:text-left', className)} {...props} />
)
DialogHeader.displayName = 'DialogHeader'

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn('text-lg font-semibold leading-none tracking-tight', className)}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog, DialogPortal, DialogOverlay, DialogClose, DialogTrigger,
  DialogContent, DialogHeader, DialogTitle, DialogDescription,
}
```

---

## Opção D — Formulário com Validação

### Estrutura padrão para formulários

```tsx
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import api from '@/services/api'

const schema = z.object({
  // campos com validação Zod
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido'),
})

type FormData = z.infer<typeof schema>

interface {NomeDoFormulario}Props {
  onSuccess?: () => void
}

export default function {NomeDoFormulario}({ onSuccess }: {NomeDoFormulario}Props) {
  const [isLoading, setIsLoading] = useState(false)

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    setIsLoading(true)
    try {
      await api.post('/v1/{endpoint}', data)
      toast.success('Salvo com sucesso!')
      reset()
      onSuccess?.()
    } catch {
      toast.error('Erro ao salvar. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="nome">Nome</Label>
        <Input id="nome" {...register('nome')} />
        {errors.nome && <p className="text-sm text-destructive">{errors.nome.message}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" {...register('email')} />
        {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
      </div>
      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Salvando...' : 'Salvar'}
      </Button>
    </form>
  )
}
```

### Tipos Zod mais usados

| Campo | Schema Zod |
|---|---|
| Texto obrigatório | `z.string().min(1, 'Campo obrigatório')` |
| Email | `z.string().email('Email inválido')` |
| Número | `z.number().min(0, 'Deve ser positivo')` |
| Número de string | `z.string().transform(Number)` |
| Booleano | `z.boolean()` |
| Enum | `z.enum(['ativo', 'inativo'])` |
| Opcional | `z.string().optional()` |
| Com regex | `z.string().regex(/^\d{5}-\d{3}$/, 'CEP inválido')` |

---

## Regras de Execução

1. **Sempre verifique** se a pasta de destino já existe antes de criar o arquivo
2. **Para rotas**, sempre atualize `src/router/index.tsx` — nunca deixe uma página sem rota registrada
3. **Para componentes shadcn**, instale o pacote Radix correspondente se necessário (informar ao usuário quais `npm install` executar)
4. **Nunca altere** arquivos de configuração (vite, tailwind, tsconfig) ao adicionar componentes
5. **Ao final**, liste os arquivos criados e os arquivos modificados separadamente
