/* Configuração do site Mais Concursados.
   Preencha os campos abaixo quando as ferramentas estiverem prontas. Campo vazio = recurso desligado. */
window.MC_CONFIG = {
  // Endereço que recebe os cadastros (formulário do Brevo, Mailchimp, RD Station, Formspree ou webhook).
  // O site envia um JSON com: email, whatsapp, interesse, origem, consentimento, data.
  leadsEndpoint: "",
  // Mailchimp (formulário incorporado): endereço "action" do formulário e nome do campo anti-robô (b_...).
  mailchimpAction: "https://maisconcursados.us13.list-manage.com/subscribe/post?u=8cefefc6b696b012af0395df7&id=596510e64a&f_id=008d00e9f0",
  mailchimpHoneypot: "b_8cefefc6b696b012af0395df7_596510e64a",
  // Link de convite do grupo ou da comunidade de WhatsApp. Quando preenchido, aparece o botão "Entrar no grupo".
  whatsappGroupUrl: "https://chat.whatsapp.com/E4UEBEedzbH2DpyvREZUoH?s=cl&p=a&mlu=4&ilr=4",
  // Link de pagamento ou de inscrição da turma Bancada BACEN (Herospark, Hotmart etc.). Vazio = botão leva à lista de espera.
  checkoutBancadaUrl: "",
  // E-mail de contato exibido na página Contato (opcional).
  contactEmail: "",
  // ID do Google Analytics 4, no formato G-XXXXXXXXXX (opcional).
  analyticsId: ""
};
