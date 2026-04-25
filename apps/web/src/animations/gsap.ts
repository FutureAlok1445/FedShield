/**
 * GSAP animation utilities for FedShield dashboard.
 * PRD §7.2 — page entrance, number count-up, gauge, sidebar, alerts.
 */
import gsap from 'gsap'

/** Page entrance — staggered cards (PRD §7.2) */
export function animateStatCards(selector = '.stat-card') {
  gsap.from(selector, {
    y: 20,
    opacity: 0,
    duration: 0.5,
    stagger: 0.08,
    ease: 'power2.out',
    clearProps: 'all',
  })
}

/** Number count-up (PRD §7.2) */
export function animateNumber(el: HTMLElement, target: number, decimals = 0) {
  gsap.from({ val: 0 }, {
    val: target,
    duration: 1.5,
    ease: 'power2.out',
    onUpdate: function () {
      el.textContent = this.targets()[0].val.toFixed(decimals)
    },
  })
}

/** Alert feed entrance (PRD §7.2) */
export function animateNewAlert(element: HTMLElement) {
  gsap.from(element, {
    x: 40,
    opacity: 0,
    duration: 0.35,
    ease: 'power2.out',
  })
  if (element.dataset.decision === 'block') {
    gsap.to(element, {
      backgroundColor: '#FEE2E2',
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      delay: 0.35,
    })
  }
}

/** Fraud score gauge needle (PRD §7.2) */
export function animateGauge(needleSelector: string, probability: number) {
  const angle = -90 + probability * 180
  gsap.to(needleSelector, {
    rotation: angle,
    transformOrigin: '50% 100%',
    duration: 1.2,
    ease: 'elastic.out(1, 0.5)',
  })
}

/** Round progress bar fill (PRD §7.2) */
export function animateProgressBar(selector: string, received: number, expected: number) {
  gsap.to(selector, {
    width: `${(received / expected) * 100}%`,
    duration: 0.5,
    ease: 'power2.out',
  })
}

/** Generic page entrance */
export function animatePageEntrance(selector = '.animate-in') {
  gsap.from(selector, {
    y: 12,
    opacity: 0,
    duration: 0.4,
    ease: 'power2.out',
  })
}
