describe('Просмотр конкретного покемона', () => {
    const host = "127.0.0.1:8000";
    it('Отображает информацию о покемоне', () => {
      cy.visit(host+'/pokemon/1') 
      cy.get('.pokemon-name')
        .should('contain', 'bulbasaur');
      cy.get('.hp-text')
        .should('contain', '45');
      cy.get('.hp-attack')
        .should('contain', '49');
      cy.get('.hp-defence')
        .should('contain', '49');
    });
  });
  