// scripts.js

// Función para animar elementos al hacer scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.fade-in');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.classList.add('visible');
        }
    });
}

// Función para inicializar los gráficos
function initCharts() {
    // Gráfico 1: Población ciega mundial
    const ctx1 = document.getElementById('grafico1').getContext('2d');
    new Chart(ctx1, {
        type: 'line',
        data: {
            labels: ['2010', '2012', '2014', '2016', '2018', '2020', '2022', '2023', '2024'],
            datasets: [{
                label: 'Población total ciega',
                data: [32, 34, 35, 37, 39, 41, 43, 44, 45],
                borderColor: '#00cc99',
                backgroundColor: 'rgba(0, 204, 153, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#d2f4e3',
                        font: {
                            size: 14
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 204, 153, 0.1)'
                    },
                    ticks: {
                        color: '#d2f4e3',
                        callback: function(value) {
                            return value + 'M';
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 204, 153, 0.1)'
                    },
                    ticks: {
                        color: '#d2f4e3'
                    }
                }
            }
        }
    });

    // Gráfico 2: Distribución por continente
    const ctx2 = document.getElementById('grafico2').getContext('2d');
    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['Asia', 'África', 'Europa', 'América del Norte', 'América del Sur', 'Oceanía'],
            datasets: [{
                data: [45, 25, 15, 8, 5, 2],
                backgroundColor: [
                    '#00cc99',
                    '#00b386',
                    '#009973',
                    '#008060',
                    '#00664d',
                    '#004d3b'
                ],
                borderWidth: 0,
                hoverOffset: 20
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart',
                animateScale: true,
                animateRotate: true
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#d2f4e3',
                        padding: 20,
                        font: {
                            size: 14
                        }
                    }
                }
            }
        }
    });

    // Gráfico 3: Distribución por edad
    const ctx3 = document.getElementById('grafico3').getContext('2d');
    new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: ['0-5 años', '6-16 años', '17-30 años', '31-64 años', '65 o más años'],
            datasets: [{
                label: 'Distribución por edad',
                data: [1.04, 3.85, 6.89, 42.61, 45.61],
                backgroundColor: [
                    '#00cc99',
                    '#00b386',
                    '#009973',
                    '#008060',
                    '#00664d'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 204, 153, 0.1)'
                    },
                    ticks: {
                        color: '#d2f4e3',
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#d2f4e3',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Observador para la sección de impacto
const impactoObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Inicializar gráficos cuando la sección es visible
            initCharts();
            // Dejar de observar una vez que los gráficos se han inicializado
            impactoObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.5 // Se activa cuando el 50% de la sección es visible
});

// Observar la sección de impacto
const impactoSection = document.getElementById('impacto');
if (impactoSection) {
    impactoObserver.observe(impactoSection);
}

// Función para animar el texto de bienvenida
function animateWelcomeText() {
    const welcomeText = document.querySelector('.tagline');
    welcomeText.style.opacity = '0';
    welcomeText.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        welcomeText.style.transition = 'opacity 1s ease, transform 1s ease';
        welcomeText.style.opacity = '1';
        welcomeText.style.transform = 'translateY(0)';
    }, 500);
}

// Función para animar los logos de sponsors
function animateSponsors() {
    const sponsors = document.querySelectorAll('.sponsor-logo');
    sponsors.forEach((sponsor, index) => {
        setTimeout(() => {
            sponsor.style.opacity = '0';
            sponsor.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                sponsor.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                sponsor.style.opacity = '1';
                sponsor.style.transform = 'scale(1)';
            }, 100);
        }, index * 200);
    });
}

// Función para manejar el scroll suave
function smoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Función para inicializar todas las animaciones
function initAnimations() {
    // Añadir clase fade-in a las secciones
    document.querySelectorAll('section').forEach(section => {
        section.classList.add('fade-in');
    });

    // Inicializar eventos
    window.addEventListener('scroll', animateOnScroll);
    window.addEventListener('load', () => {
        animateOnScroll();
        animateWelcomeText();
        animateSponsors();
    });

    // Inicializar scroll suave
    smoothScroll();
}

// Funcionalidad de la galería
function initGallery() {
    const filtros = document.querySelectorAll('.filtro-btn');
    const items = document.querySelectorAll('.galeria-item');
    const modal = document.querySelector('.galeria-modal');
    const modalImg = document.querySelector('.modal-img');
    const modalTitle = document.querySelector('.modal-info h3');
    const modalDesc = document.querySelector('.modal-info p');
    const cerrarModal = document.querySelector('.cerrar-modal');

    // Filtrado de imágenes
    filtros.forEach(filtro => {
        filtro.addEventListener('click', () => {
            // Actualizar botones activos
            filtros.forEach(f => f.classList.remove('active'));
            filtro.classList.add('active');

            const categoria = filtro.dataset.filtro;

            items.forEach(item => {
                if (categoria === 'todos' || item.dataset.categoria === categoria) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });

    // Abrir modal
    items.forEach(item => {
        const verMasBtn = item.querySelector('.ver-mas');
        verMasBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const img = item.querySelector('img');
            const title = item.querySelector('h3').textContent;
            const desc = item.querySelector('p').textContent;

            modalImg.src = img.src;
            modalImg.alt = img.alt;
            modalTitle.textContent = title;
            modalDesc.textContent = desc;

            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
    });

    // Cerrar modal
    cerrarModal.addEventListener('click', () => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    });

    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });

    // Animación inicial de las imágenes
    items.forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
        }, index * 100);
    });
}

// Funcionalidad del carrusel
document.addEventListener('DOMContentLoaded', () => {
    const carrusel = document.querySelector('.carrusel-container');
    const slides = document.querySelectorAll('.carrusel-slide');
    const prevBtn = document.querySelector('.carrusel-btn.prev');
    const nextBtn = document.querySelector('.carrusel-btn.next');
    
    let currentSlide = 0;
    const totalSlides = slides.length;

    function updateCarrusel() {
        carrusel.style.transform = `translateX(-${currentSlide * 100}%)`;
    }

    prevBtn.addEventListener('click', () => {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        updateCarrusel();
    });

    nextBtn.addEventListener('click', () => {
        currentSlide = (currentSlide + 1) % totalSlides;
        updateCarrusel();
    });

    // Navegación con teclado
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            prevBtn.click();
        } else if (e.key === 'ArrowRight') {
            nextBtn.click();
        }
    });
});

// Funcionalidad de texto a voz
let speechSynthesis = window.speechSynthesis;
let isReading = false;
let currentUtterance = null;
let sectionsToRead = ['quienes', 'consiste', 'tecnico', 'contacto'];
let currentSectionIndex = 0;

function getSectionContent(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return '';
    
    let content = '';
    const heading = section.querySelector('h2');
    const paragraphs = section.querySelectorAll('p:not(.rol):not(.descripcion)');
    
    if (heading) content += heading.textContent + '. ';
    paragraphs.forEach(p => {
        content += p.textContent + '. ';
    });
    
    return content;
}

function readNextSection() {
    if (currentSectionIndex >= sectionsToRead.length) {
        currentSectionIndex = 0;
        isReading = false;
        updateReadButton();
        return;
    }

    const sectionId = sectionsToRead[currentSectionIndex];
    const content = getSectionContent(sectionId);
    
    if (content) {
        currentUtterance = new SpeechSynthesisUtterance(content);
        currentUtterance.lang = 'es-ES';
        currentUtterance.rate = 1;
        
        currentUtterance.onend = () => {
            currentSectionIndex++;
            if (isReading) {
                setTimeout(readNextSection, 500); // Pequeña pausa entre secciones
            }
        };
        
        speechSynthesis.speak(currentUtterance);
    } else {
        currentSectionIndex++;
        readNextSection();
    }
}

function updateReadButton() {
    const readButton = document.getElementById('readButton');
    if (readButton) {
        if (isReading) {
            readButton.classList.add('playing');
            readButton.innerHTML = '<i class="fas fa-stop"></i> Detener lectura <span class="shortcut">(R)</span>';
        } else {
            readButton.classList.remove('playing');
            readButton.innerHTML = '<i class="fas fa-volume-up"></i> Leer contenido <span class="shortcut">(R)</span>';
        }
    }
}

function toggleReading() {
    if (isReading) {
        speechSynthesis.cancel();
        isReading = false;
        currentSectionIndex = 0;
    } else {
        isReading = true;
        readNextSection();
    }
    updateReadButton();
}

// Manejo de teclado
document.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 'r' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
        e.preventDefault();
        toggleReading();
    }
});

// Inicializar el botón de lectura
document.addEventListener('DOMContentLoaded', () => {
    const readButton = document.getElementById('readButton');
    if (readButton) {
        readButton.addEventListener('click', toggleReading);
    }
});

// Inicializar todo cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initAnimations();
    initGallery();
}); 