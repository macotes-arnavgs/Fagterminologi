// Henter referanser til elementene
const radioButtons = document.querySelectorAll('input[name="mastery"]');
const userTextarea = document.getElementById('user-def');
const showDefBtn = document.getElementById('show-def-btn');
const dbDefTextarea = document.getElementById('db-def');

const userForrigeDefTextarea = document.getElementById('user-forrige-def');
const showForrigeDefBtn = document.getElementById('show-forrige-def-btn');

// Logikk for å aktivere/deaktivere tekstboks basert på radio buttons
radioButtons.forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.value === 'none') {
            userTextarea.disabled = true;
            userTextarea.value = ""; // Tømmer boksen hvis de ikke har peiling
        } else {
            userTextarea.disabled = false;
        }
    });
});

// Logikk for å vise definisjonen fra databasen
showDefBtn.addEventListener('click', () => {
    const fasit = showDefBtn.getAttribute('data-def');
    dbDefTextarea.value = fasit;
});

// Logikk for å vise brukerens forrige definisjon
showForrigeDefBtn.addEventListener('click', () => {
    const forrigeDefinisjon = showForrigeDefBtn.getAttribute('data-forrige-def');
    
    // Sjekker om tekstboksen er tom
    if (userForrigeDefTextarea.value === "") {
        // Hvis den er tom, vis teksten
        userForrigeDefTextarea.value = forrigeDefinisjon;
    } else {
        // Hvis den ikke er tom, skjul teksten (tøm boksen)
        userForrigeDefTextarea.value = "";
    }
});
/*
showForrigeDefBtn.addEventListener('click', () => {
    const forrigeDefinisjon = showForrigeDefBtn.getAttribute('data-forrige-def');
    userForrigeDefTextarea.value = forrigeDefinisjon;
}); */