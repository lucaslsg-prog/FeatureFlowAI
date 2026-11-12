Feature: Tela de Login

  Background:
    Given que o usuário está na tela de login da aplicação web corporativa

  Scenario: Login realizado com credenciais válidas
    Given que o usuário informa o e-mail "usuario.valido@exemplo.com"
    And a senha "SenhaForte1!"
    When o usuário clicar no botão de login
    Then o acesso é concedido
    And a sessão é mantida conforme a política da aplicação
    And o evento de autenticação é registrado no log

  Scenario Outline: Login negado com credenciais inválidas
    Given que o usuário informa o e-mail "<email>"
    And a senha "<senha>"
    When o usuário clicar no botão de login
    Then é exibida a mensagem "Credenciais inválidas"
    And o acesso é negado

    Examples:
      | email                     | senha          |
      | usuario.invalido@exemplo.com | SenhaIncorreta |
      | usuario.valido@exemplo.com   | senhaerrada    |
      | usuario.invalido@exemplo.com | senhaerrada    |

  Scenario: Bloqueio ocorre após 5 tentativas de login consecutivas com credenciais inválidas
    Given que o usuário informa o e-mail "usuario.valido@exemplo.com"
    And a senha incorreta "SenhaErrada1!"
    When o usuário tentar fazer login 5 vezes consecutivas
    Then o acesso é bloqueado por 15 minutos
    And é exibida a mensagem "Acesso bloqueado por 15 minutos devido a múltiplas tentativas falhas"

  Scenario: Campo e-mail valida formato incorreto
    Given que o usuário informa o e-mail "usuario#exemplo.com"
    When o usuário tentar preencher o campo e-mail
    Then a validação do campo e-mail falha
    And o sistema exibe mensagem de erro "Formato de e-mail inválido"

  Scenario: Campo senha é mascarado
    Given que o usuário está na tela de login
    When o usuário digitar a senha "SenhaForte1!"
    Then os caracteres da senha são exibidos como mascarados

  Scenario: Recuperação de senha envia e-mail corretamente
    Given que o usuário está na tela de login
    When o usuário clicar na opção "Esqueci minha senha"
    And informar o e-mail "usuario.valido@exemplo.com"
    Then o sistema envia um link de redefinição de senha para o e-mail informado

  Scenario: Usuário inativo tenta autenticar
    Given que o usuário "usuario.inativo@exemplo.com" está com status inativo
    When o usuário informar o e-mail "usuario.inativo@exemplo.com"
    And a senha correta "SenhaForte1!"
    And clicar no botão de login
    Then o acesso é negado
    And é exibida a mensagem "Usuário inativo não pode autenticar"

  Scenario Outline: Senha atende aos requisitos mínimos de segurança
    Given que o usuário informa a senha "<senha>"
    When o sistema valida a senha
    Then a senha é considerada válida

    Examples:
      | senha           |
      | SenhaForte1!    |
      | A1b2c3d4$       |

  Scenario Outline: Senha não atende aos requisitos mínimos de segurança
    Given que o usuário informa a senha "<senha>"
    When o sistema valida a senha
    Then a senha é considerada inválida

    Examples:
      | senha       |
      | senha       |
      | senha123    |
      | SENHA123!   |
      | Senha123    |
      | Senha!      |

  Scenario: Tempo de resposta da autenticação é inferior a 2 segundos
    Given que o usuário informa o e-mail "usuario.valido@exemplo.com"
    And a senha "SenhaForte1!"
    When o usuário clicar no botão de login
    Then o sistema responde em menos de 2 segundos

  Scenario: Comunicação protegida por HTTPS/TLS na tela de login
    Given que o usuário está na tela de login
    When o usuário acessar a página
    Then a comunicação ocorre via HTTPS/TLS

  Scenario Outline: Compatibilidade da tela de login com navegadores suportados
    Given que o usuário está usando o navegador "<navegador>"
    When o usuário acessa a tela de login
    Then a tela de login é exibida corretamente

    Examples:
      | navegador |
      | Chrome    |
      | Edge      |
      | Firefox   |

  Scenario: Expiração de senha conforme política corporativa impede login
    Given que o usuário "usuario.expirado@exemplo.com" tem a senha expirada conforme política corporativa
    When o usuário informar o e-mail "usuario.expirado@exemplo.com"
    And a senha correta "SenhaForte1!"
    And clicar no botão de login
    Then o acesso é negado
    And é exibida a mensagem "Senha expirada, por favor redefina sua senha"

  Scenario: Manutenção da sessão conforme política da aplicação após login
    Given que o usuário realizou login com sucesso
    When o usuário permanece inativo por tempo inferior ao limite da política de sessão
    Then a sessão permanece ativa

  Scenario: Bloqueio após 5 tentativas de login com e-mails inválidos
    Given que o usuário informa o e-mail "invalido@exemplo"
    And a senha qualquer "Qualquer1!"
    When o usuário tentar fazer login 5 vezes consecutivas
    Then o acesso é bloqueado por 15 minutos
    And é exibida a mensagem "Acesso bloqueado por 15 minutos devido a múltiplas tentativas falhas"
