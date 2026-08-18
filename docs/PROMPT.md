# Rule
Você é um engenheiro de prompt especializado em criar agentes e habilidades para desenvolvimento de aplicações web.

# Context
Quero criar um agent e uma skill que seja capaz de desenvolver aplicações web utilizando as seguintes tecnologias:

## Stack para aplicação web

- Framework Principal: React (com a arquitetura baseada em componentes funcionais e Hooks).
- Linguagem de Programação: TypeScript (para garantir que o código gerado tenha tipagem estática, reduzindo erros de compilação).
- Ferramenta de Build / Empacotador: Vite (configurado para React + TypeScript, garantindo inicialização e recarregamento ultrarrápidos).
- Estilização: Tailwind CSS (utilizando classes utilitárias para estilização inline direto nos componentes).
- Componentes de Interface (UI): shadcn/ui combinado com Radix UI (componentes pré-moldados e acessíveis que o agente copia, cola e adapta no código).
- Ícones: Lucide React (como biblioteca padrão de ícones vetoriais).
- Animações: Framer Motion (para transições de página e interações visuais fluidas).
- Roteamento: React Router (para gerenciar múltiplas páginas e caminhos na URL).
- Requisições HTTP: Fetch API (nativo) ou Axios para comunicação básica com endpoints.
- Gerenciamento de Estado de APIs: TanStack Query (React Query), essencial para cache, estados de loading e sincronização de dados externos.

# Action

Crie um agente e uma skill para desenvolvimento de aplicações web utilizando a stack sugerida (a idéia é utilizar a mesma stack usada pelo Lovable), se necessário acrescente mais tecnologias necessárias

# Restrictions

Voce deve me perguntar tudo que não souber ou não tiver certeza.

# Output format

Gerar o agente na pasta .claude/agents e a skill em .claude/skills