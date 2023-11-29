describe('Бой между покемонами', () => {
    const host = "127.0.0.1:8000";
    it('Проходит бой между двумя покемонами', () => {
      cy.visit(host+'/pokemon/1')
      cy.get('.select-button').click()

      cy.visit(host+'/pokemon/2') 
      cy.get('.fight-button').click() 
  
      // Процесс боя
      const attack = () => {
        cy.get('.attack-input').type('5') 
        cy.get('.attack-button').click()
        cy.get('.attack-message').then(($status) => {
          if ($status.text().includes('Атака прошла успешно') || $status.text().includes('Вас атаковали')) {
            attack();
          }
        });
      };
      attack();
  
      // Завершение боя
      cy.get('.email-input').type('vlad-057@mail.ru') 
      cy.get('.send-email-button').click()
    });
  });
  