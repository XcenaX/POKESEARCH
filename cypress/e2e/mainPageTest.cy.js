describe('Список покемонов на главной странице', () => {
    const host = "127.0.0.1:8000";
    it('Отображает список покемонов', () => {
      cy.visit(host+'/')
      cy.get('ul.list-unstyled a')
        .should('have.length', 20);
    });
  });
  