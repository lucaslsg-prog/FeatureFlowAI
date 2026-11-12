# Fit Insight Test Cases Generator

Ferramenta responsável por automatizar a geração de casos de teste a partir de documentos de requisitos utilizando IA (Fit Insight), com posterior integração ao Jira e Xray.

O objetivo é transformar documentos funcionais em casos de teste estruturados e padronizados, reduzindo esforço manual e aumentando a produtividade e a consistência dos artefatos de QA.

---

# Arquitetura

O projeto segue princípios de separação de responsabilidades inspirados em Clean Architecture.

```text
app/
config/
domain/
integrations/
services/
utils/
```

Cada camada possui uma responsabilidade específica, evitando acoplamento excessivo e facilitando manutenção e evolução.

---

# Fluxo Geral da Aplicação

```text
Documento de Requisitos (.docx)
            │
            ▼
      FileService
            │
            ▼
 Upload para Fit Insight
            │
            ▼
       Prompt + IA
            │
            ▼
 JSON de Casos de Teste
            │
            ▼
Validação e Normalização
            │
            ▼
      Entidade TestCase
            │
            ▼
     Jira / Xray APIs
            │
            ▼
 Criação de Test Set e Test Cases
```

---

# Estrutura do Projeto

```text
app/
├── main.py

config/
├── settings.py

domain/
├── test_case.py

integrations/
├── fit_insight_client.py
├── jira_client.py
└── xray_client.py

services/
├── file_service.py
├── test_case_pipeline.py
├── gherkin_test_case_pipeline.py
└── playwright_bdd_pipeline.py

utils/
├── prompts.py
└── sanitize.py
```

---

# Responsabilidade das Camadas

| Camada | Responsabilidade |
|----------|----------|
| app | Inicialização e orquestração da aplicação |
| config | Configurações e variáveis de ambiente |
| domain | Entidades do negócio |
| integrations | Comunicação com APIs externas |
| services | Regras e fluxos do negócio |
| utils | Funções auxiliares reutilizáveis |

Uma regra simples para futuras implementações:

```text
domain       → O que o sistema manipula
services     → O que o sistema faz
integrations → Com quem o sistema conversa
utils        → Funções auxiliares
config       → Como o sistema é configurado
app          → Como o sistema inicia
```

---

# Diretórios e Arquivos

## app/

Contém os pontos de entrada da aplicação.

Responsabilidades:

- Inicializar a aplicação
- Montar dependências
- Executar o fluxo principal
- Tratar exceções globais
- Coordenar os serviços

### Arquivos

#### main.py

Ponto de entrada da aplicação.

Responsável por:

- Carregar configurações
- Inicializar clientes
- Criar serviços
- Processar documentos
- Criar Test Sets
- Criar Test Cases
- Executar o fluxo completo

---

## config/

Centraliza todas as configurações da aplicação.

Objetivos:

- Evitar valores hardcoded
- Facilitar deploy
- Centralizar variáveis sensíveis

### Arquivos

#### settings.py

Responsável por ler:

- URLs das APIs
- Usuários
- Tokens
- Credenciais
- Configurações globais

Exemplos:

```env
JIRA_URL=
JIRA_USER=
JIRA_API_TOKEN=
XRAY_CLIENT_ID=
XRAY_CLIENT_SECRET=
```

---

## domain/

Contém as entidades de negócio.

Entidades representam os dados do domínio da aplicação e não devem depender de APIs, frameworks ou bibliotecas externas.

### Arquivos

#### test_case.py

Representa um Caso de Teste.

Exemplo:

```python
TestCase(
    descricao="Cadastrar Produto",
    acoes=["Acessar tela", "Salvar"],
    dados={"produto": "Notebook"},
    resultadoEsperado=["Produto criado"]
)
```

Responsabilidades:

- Estruturar os dados
- Garantir consistência
- Validar formato esperado
- Converter entre objeto e dicionário

---

## integrations/

Responsável pela integração com sistemas externos.

Todo código que consome APIs deve ficar nesta camada.

---

### fit_insight_client.py

Cliente responsável pela comunicação com o Fit Insight.

Funções:

- Upload de documentos
- Envio de prompts
- Recebimento de respostas da IA
- Gerenciamento de chamadas da API

---

### jira_client.py

Cliente responsável pela comunicação com o Jira.

Funções:

- Criação de Issues
- Consulta de projetos
- Consulta de metadados
- Atualização de informações

---

### xray_client.py

Cliente responsável pela comunicação com o Xray.

Funções:

- Criação de Test Sets
- Associação de Test Cases
- Operações específicas do Xray

---

## services/

Camada responsável pelas regras de negócio e pelos fluxos da aplicação.

Essa camada coordena o trabalho entre entidades e integrações.

---

### file_service.py

Responsável por manipular documentos.

Funções:

- Leitura de arquivos
- Validação de existência
- Tratamento de nomes
- Preparação para upload

---

### test_case_pipeline.py

Principal fluxo da aplicação.

Responsabilidades:

1. Receber documento
2. Validar arquivo
3. Fazer upload para o Fit Insight
4. Enviar prompt para a IA
5. Receber resposta
6. Extrair JSON
7. Sanitizar resposta
8. Validar estrutura dos dados
9. Criar objetos TestCase
10. Retornar casos de teste normalizados

Este componente é considerado o coração da aplicação.

---

#### gherkin_test_case_pipeline.py

Gera cenários de teste em Gherkin a partir de documentos de requisitos.

#### playwright_bdd_pipeline.py

Converte o arquivo `.feature` para `.docx`, faz upload do documento para o Fit
Insight e associa esse arquivo à conversa que gera as definições de etapas
TypeScript para Playwright-BDD.

---

## utils/

Contém utilitários reutilizáveis.

O objetivo é evitar duplicação de código e manter responsabilidades organizadas.

---

### prompts.py

Centraliza os prompts utilizados pela IA.

Benefícios:

- Facilidade de manutenção
- Evolução dos prompts
- Reutilização entre pipelines

---

### sanitize.py

Responsável pela limpeza do conteúdo retornado pela IA.

Funções:

- Remover caracteres inválidos
- Corrigir formatações conhecidas
- Garantir JSON válido
- Aumentar robustez do parsing

---

# Princípios Utilizados

## Separação de Responsabilidades

Cada módulo deve possuir apenas uma responsabilidade principal.

Exemplos:

- Integrações → APIs
- Serviços → Fluxos de negócio
- Entidades → Regras de domínio

---

## Baixo Acoplamento

As camadas possuem dependências mínimas.

Benefícios:

- Facilidade de refatoração
- Menos efeito cascata
- Código mais previsível

---

## Alta Coesão

Cada arquivo possui uma responsabilidade claramente definida.

Isso facilita:

- Leitura
- Manutenção
- Evolução

---

## Testabilidade

Como integrações estão isoladas, é possível:

- Mockar APIs
- Testar regras de negócio separadamente
- Executar testes unitários sem acessar Jira ou Fit Insight

---

# Configuração

## 1. Criar arquivo .env

Utilize um arquivo baseado no modelo:

```bash
cp .env.example .env
```

Preencha todas as credenciais necessárias.

---

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 3. Executar a aplicação

```bash
python -m app.main
```

O fluxo existente de casos JSON continua sendo o padrão. Para executar as novas
pipelines, use:

```bash
# Gerar casos JSON e integrar os resultados ao Jira/Xray
python -m app.main --pipeline json

# Gerar arquivos Gherkin (.feature) dos documentos em DOCS_PATH
python -m app.main --pipeline gherkin

# Gerar TypeScript Playwright-BDD a partir dos .feature em OUTPUT_DIR
python -m app.main --pipeline playwright-bdd

# Informar outro diretório de arquivos Gherkin
python -m app.main --pipeline playwright-bdd --gherkin-dir caminho/para/features

# Executar as duas pipelines em sequência e salvar .feature e .steps.ts em OUTPUT_DIR
python -m app.main --pipeline all
```

> **Importante:** `--pipeline all` não envia requests para a API do Jira/Xray.
> Esse modo executa apenas a geração de Gherkin, `.docx` e TypeScript
> Playwright-BDD. Para criar o Test Set, os testes Xray e associá-los no Jira,
> use obrigatoriamente `--pipeline json`.

No pipeline `json`, o Jira cria primeiro o registro com o issue type `Test Set`.
Caso esse tipo não esteja disponível para o projeto, usa automaticamente `Task`.
Para cada caso de teste, tenta primeiro o issue type `Xray Test` e, quando ele
não estiver disponível, cria o issue como `Task`. Nenhuma configuração adicional
é necessária no `.env`. Quando o issue é criado como `Task`, o sistema não chama
a API de autenticação ou importação do Xray. Os casos gerados são transformados
em texto Gherkin e inseridos como descrição da Task, incluindo dados, ações e
resultados esperados; os passos não são importados como testes Xray.

As opções `gherkin`, `playwright-bdd` e `all` precisam das configurações do Fit
Insight e dos caminhos `DOCS_PATH`/`OUTPUT_DIR`, mas não exigem credenciais do
Jira/Xray.

### Como o `main.py` executa cada pipeline

O `main.py` interpreta `--pipeline` com `argparse` e direciona a execução para um
dos fluxos abaixo. Se a opção não for informada, o valor padrão é `json`, mantendo
o comportamento original:

| Opção | Entrada | Processamento | Saída |
|---|---|---|---|
| `json` | Documentos em `DOCS_PATH` | Gera casos JSON e os integra ao Jira/Xray | Test Set e testes no Jira/Xray |
| `gherkin` | Documentos em `DOCS_PATH` | Gera cenários Gherkin | Arquivos `.feature` em `OUTPUT_DIR` |
| `playwright-bdd` | Arquivos `.feature` em `OUTPUT_DIR` ou `--gherkin-dir` | Converte para `.docx`, envia ao Fit Insight e gera as etapas TypeScript | Arquivos `.docx` e `.steps.ts` em `OUTPUT_DIR` |
| `all` | Documentos em `DOCS_PATH` | Gera Gherkin e, em seguida, converte para `.docx` e gera TypeScript | Arquivos `.feature`, `.docx` e `.steps.ts` em `OUTPUT_DIR` |

No início, o programa carrega as configurações e cria o cliente do Fit Insight.
As funções auxiliares separam as responsabilidades: `_run_json_pipeline`
preserva o fluxo integrado com Jira/Xray; `_run_generated_pipelines` executa os
novos fluxos; `_create_fit_client` centraliza a criação do cliente.

Para `gherkin` e `all`, o `FileService` percorre os documentos de `DOCS_PATH`.
Cada resultado é salvo usando o nome original normalizado, com extensão
`.feature`. Na opção `all`, o arquivo `.feature` também é convertido em `.docx`,
enviado ao Fit Insight e associado à conversa que gera o arquivo `.steps.ts`.

Para `playwright-bdd`, nenhum documento de requisitos é processado: o programa
lê arquivos `.feature` já existentes no diretório indicado por `--gherkin-dir`.
Se esse argumento não for informado, usa `OUTPUT_DIR`. A busca é pelos arquivos
`.feature` diretamente nesse diretório. Os arquivos TypeScript gerados são
gravados em `OUTPUT_DIR`.

Se o Fit Insight retornar um erro HTTP ao gerar as etapas, a mensagem inclui o
detalhe retornado pela API para ajudar a identificar a causa. Como o `.feature`
já foi salvo antes dessa etapa, tente novamente sem regenerar o Gherkin:

```bash
python -m app.main --pipeline playwright-bdd --gherkin-dir output
```

A opção `playwright-bdd` salva o documento `.docx` convertido em `OUTPUT_DIR` e
envia esse arquivo à API antes de solicitar as definições de etapas. A conversão
mantém o conteúdo Gherkin em parágrafos separados, incluindo linhas vazias.

`Settings.load` exige as credenciais do Jira/Xray somente na opção `json`.
Todas as opções continuam exigindo as configurações de acesso ao Fit Insight.
`DOCS_PATH` e `OUTPUT_DIR` podem ser definidos no `.env`; por padrão, são
`MDSC_requirements` e `output`, respectivamente.

---

# Exemplo de Caso de Teste Gerado

```json
{
  "descricao": "Cadastrar Produto com nome válido",
  "acoes": [
    "Acessar tela de Produtos",
    "Clicar em Add Product"
  ],
  "dados": {
    "product": "Produto Novo"
  },
  "resultadoEsperado": [
    "Produto cadastrado com sucesso"
  ]
}
```

---

# Benefícios da Arquitetura

- Separação clara de responsabilidades
- Fácil manutenção
- Facilidade para criar testes automatizados
- Menor acoplamento entre módulos
- Integrações isoladas
- Evolução mais simples do sistema
- Código mais organizado e escalável
- Maior legibilidade para novos desenvolvedores

---

# Roadmap Futuro

Possíveis evoluções:

- Suporte a múltiplos modelos de IA
- Geração de cenários Gherkin
- Integração automática com Playwright
- Integração direta com Xray GraphQL
- Exportação para Excel
- Versionamento de prompts
- Pipeline de validação dos casos gerados