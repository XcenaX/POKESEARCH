import type { PokemonData } from '../index';

describe('Pokemon List and Details Tests', () => {
    let pokemonFixture: PokemonData;

    before(() => {
        cy.fixture('charizard.json').then((data) => {
            pokemonFixture = data;
        });
    });

    beforeEach(() => {
        cy.intercept('GET', 'http://localhost:8000/pokemons/?limit=1300', { fixture: 'pokemons.json' }).as('getPokemons');

        cy.intercept('GET', 'http://localhost:8000/pokemon/*', (req) => {
            const pokemonName = req.url.split('/').pop();
            const responseData = { ...pokemonFixture, name: pokemonName };
            req.reply(responseData);
        }).as('getPokemonDetails');
    });

    it('loads and displays details for each pokemon', () => {
        cy.visit('/');
        cy.wait('@getPokemons');

        cy.get('.pokemon-list-item').should('have.length.at.least', 1);
    });

    it('handles 404 error for non-existent pokemon details', () => {
        cy.visit('/');
        cy.wait('@getPokemons');

        const nonExistentPokemonName = 'NonExistentPokemon';
        cy.intercept('GET', `http://localhost:8000/pokemon/${nonExistentPokemonName}`, {
            statusCode: 404,
            body: 'Not Found'
        }).as('getPokemonDetailsFail');

        cy.get('.search-input').type(nonExistentPokemonName);
        cy.get('.button-search').click();

        cy.wait('@getPokemonDetailsFail');
        cy.contains('Покемон не найден').should('be.visible');
    });

    it('allows the user to search for pokemons', () => {
        cy.visit('/');
        cy.wait('@getPokemons');

        cy.get('.search-input').type('Charizard');
        cy.get('.button-search').click();
        cy.get('.pokemon-view').should('contain', 'Charizard');
    });

    it('paginates the list of pokemons', () => {
        cy.visit('/');
        cy.wait('@getPokemons');

        cy.get('.pagination .button').should('exist');

        cy.get('.pokemon-list-item').first().invoke('text').then((firstPokemonNameOnFirstPage) => {
            cy.get('.pagination .button').eq(1).click();
            cy.get('.pagination .button').eq(1).should('have.class', 'active');
            cy.get('.pokemon-list-item').first().invoke('text').then((firstPokemonNameOnSecondPage) => {
                expect(firstPokemonNameOnFirstPage).not.to.equal(firstPokemonNameOnSecondPage);
            });
        });
    });

    it('navigates to the pokemon details page on card click', () => {
        cy.visit('/');
        cy.wait('@getPokemons');
        cy.wait('@getPokemonDetails');

        cy.get('.pokemon-list-item').first().find('.pokemon-list-item-name').invoke('text').then((pokemonName) => {
            cy.get('.pokemon-list-item').first().click();

            cy.url().should('include', `/pokemon/${pokemonName.trim()}`);

            cy.get('.pokemon-info-name').should('contain', pokemonName.trim());
            cy.get('.pokemon-info-image img').should('have.attr', 'src');

            cy.get('.pokemon-stat').should('have.length.at.least', 1);
            cy.get('.pokemon-stat-name').should('exist');
            cy.get('.pokemon-stat-value').should('exist');
        });
    });


    it('handles errors gracefully', () => {
        cy.intercept('GET', 'http://localhost:8000/pokemons/?limit=1300', { statusCode: 500 }).as('getPokemonsFail');
        cy.visit('/');
        cy.wait('@getPokemonsFail');
    });
});
