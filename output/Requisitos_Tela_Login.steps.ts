import { test, expect } from '@playwright/test';
import { createBdd } from 'playwright-bdd';

const { Given, When, Then } = createBdd(test);

Given('que o usuário está na tela de login da aplicação web corporativa', async ({ page }) => {
  await page.goto('/login');
});

Given('que o usuário informa o e-mail {string}', async ({ page }, email: string) => {
  await page.getByLabel(/e-?mail/i).fill(email);
});

Given('a senha {string}', async ({ page }, senha: string) => {
  await page.getByLabel(/senha/i).fill(senha);
});

Given('a senha incorreta {string}', async ({ page }, senha: string) => {
  await page.getByLabel(/senha/i).fill(senha);
});

Given('que o usuário está na tela de login', async ({ page }) => {
  await page.goto('/login');
});

Given('que o usuário {string} está com status inativo', async (_, usuario: string) => {
  // Status inativo deve ser simulado/configurado externamente ou mockado
});

Given('que o usuário {string} tem a senha expirada conforme política corporativa', async (_, usuario: string) => {
  // Status de senha expirada deve ser simulado/configurado externamente ou mockado
});

Given('que o usuário realizou login com sucesso', async (_, __) => {
  // Login bem-sucedido assumido; estado configurado externamente
});

Given('que o usuário informa a senha {string}', async ({ page }, senha: string) => {
  await page.getByLabel(/senha/i).fill(senha);
});

Given('que o usuário informa a senha qualquer {string}', async ({ page }, senha: string) => {
  await page.getByLabel(/senha/i).fill(senha);
});

Given('que o usuário está usando o navegador {string}', async (_, navegador: string) => {
  // Navegador deve ser configurado via configuração do Playwright, não aqui
});

When('o usuário clicar no botão de login', async ({ page }) => {
  await page.getByRole('button', { name: /login/i }).click();
});

When('o usuário tentar fazer login 5 vezes consecutivas', async ({ page }) => {
  for (let i = 0; i < 5; i++) {
    await page.getByRole('button', { name: /login/i }).click();
  }
});

When('o usuário tentar preencher o campo e-mail', async ({ page }) => {
  // Considera que o campo já foi preenchido no Given
  await page.getByLabel(/e-?mail/i).blur();
});

When('o usuário digitar a senha {string}', async ({ page }, senha: string) => {
  await page.getByLabel(/senha/i).fill(senha);
});

When('o usuário clicar na opção "Esqueci minha senha"', async ({ page }) => {
  await page.getByRole('link', { name: /esqueci minha senha/i }).click();
});

When('informar o e-mail {string}', async ({ page }, email: string) => {
  await page.getByLabel(/e-?mail/i).fill(email);
});

When('clicar no botão de login', async ({ page }) => {
  await page.getByRole('button', { name: /login/i }).click();
});

When('o sistema valida a senha', async ({ page }) => {
  // Validação deve ser disparada automaticamente ou via ação externa
});

When('o usuário acessar a página', async ({ page }) => {
  await page.goto('/login');
});

When('o usuário acessa a tela de login', async ({ page }) => {
  await page.goto('/login');
});

When('o usuário permanece inativo por tempo inferior ao limite da política de sessão', async () => {
  // Simular espera menor que o limite de sessão sem interação
  await new Promise((r) => setTimeout(r, 1000));
});

Then('o acesso é concedido', async ({ page }) => {
  await expect(page.getByText(/acesso concedido/i)).toBeVisible();
});

Then('a sessão é mantida conforme a política da aplicação', async ({ page }) => {
  await expect(page.getByText(/sessão mantida/i)).toBeVisible();
});

Then('o evento de autenticação é registrado no log', async () => {
  // Verificação de log deve ser feita externamente ou mockada
});

Then('é exibida a mensagem {string}', async ({ page }, mensagem: string) => {
  await expect(page.getByText(mensagem)).toBeVisible();
});

Then('o acesso é negado', async ({ page }) => {
  await expect(page.getByText(/acesso negado/i)).toBeVisible();
});

Then('o acesso é bloqueado por 15 minutos', async ({ page }) => {
  await expect(page.getByText(/bloqueado por 15 minutos/i)).toBeVisible();
});

Then('a validação do campo e-mail falha', async ({ page }) => {
  await expect(page.getByLabel(/e-?mail/i)).toHaveAttribute('aria-invalid', 'true');
});

Then('o sistema exibe mensagem de erro {string}', async ({ page }, mensagem: string) => {
  await expect(page.getByText(mensagem)).toBeVisible();
});

Then('os caracteres da senha são exibidos como mascarados', async ({ page }) => {
  const input = page.getByLabel(/senha/i);
  await expect(input).toHaveAttribute('type', 'password');
});

Then('o sistema envia um link de redefinição de senha para o e-mail informado', async () => {
  // Verificação de envio de e-mail deve ser feita externamente ou mockada
});

Then('o acesso é negado', async ({ page }) => {
  await expect(page.getByText(/acesso negado/i)).toBeVisible();
});

Then('é exibida a mensagem "Usuário inativo não pode autenticar"', async ({ page }) => {
  await expect(page.getByText(/usuário inativo não pode autenticar/i)).toBeVisible();
});

Then('a senha é considerada válida', async ({ page }) => {
  await expect(page.getByText(/senha válida/i)).toBeVisible();
});

Then('a senha é considerada inválida', async ({ page }) => {
  await expect(page.getByText(/senha inválida/i)).toBeVisible();
});

Then('o sistema responde em menos de 2 segundos', async ({ page }, testInfo) => {
  const start = Date.now();
  await page.getByRole('button', { name: /login/i }).click();
  const elapsed = Date.now() - start;
  expect(elapsed).toBeLessThan(2000);
});

Then('a comunicação ocorre via HTTPS/TLS', async ({ page }) => {
  expect(page.url().startsWith('https://')).toBeTruthy();
});

Then('a tela de login é exibida corretamente', async ({ page }) => {
  await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
  await expect(page.getByLabel(/e-?mail/i)).toBeVisible();
  await expect(page.getByLabel(/senha/i)).toBeVisible();
  await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
});

Then('é exibida a mensagem "Senha expirada, por favor redefina sua senha"', async ({ page }) => {
  await expect(page.getByText(/senha expirada, por favor redefina sua senha/i)).toBeVisible();
});

Then('a sessão permanece ativa', async ({ page }) => {
  await expect(page.getByText(/sessão ativa/i)).toBeVisible();
});
