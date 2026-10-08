---
title: "An op-amp is the one entry that breaks the symmetry of the circuit matrix"
date: 2026-10-10
blurb: "Resistors alone give a symmetric matrix, and no node can rise above the source (2000 random networks). One op-amp adds one row with no mirror, and gain appears. The supply pays for it, feedback makes it linear, and the matrix happily solves an unstable circuit."
tags: ["electronics", "linear-algebra", "analog", "feedback"]
hero: /posts/opamp.png
code: /posts/opamp.py
draft: false
---

I never understood op-amps from the usual rules ("the inputs draw no current, the output does whatever makes the inputs equal"). Those rules are conclusions. Here is where they come from.

## A circuit at rest is a balance, and the balance is a matrix

At every junction (a **node**), the current flowing in equals the current flowing out. That is Kirchhoff's current law, and it is charge conservation: charge can't pile up on a wire. A resistor carries current $(v_a - v_b)/R$, so each node gives one linear equation in the node voltages. All nodes together:

$$G\,v = i,$$

where $v$ is the list of node voltages, $i$ the currents pushed in from outside, and $G$ the **conductance matrix** ($1/R$ values). SPICE, the standard circuit simulator, solves exactly this (modified nodal analysis, Ho, Ruehli & Brennan 1975). My 100-line version is in [the script](/posts/opamp.py).

Two facts about resistor-only circuits:

1. **$G$ is symmetric.** The resistor between nodes a and b puts the same $-1/R$ at position (a,b) and (b,a). Measured over 2000 random networks: $\max|G - G^T| = 0$.
2. **No node can exceed the source.** Rearrange one row of $Gv = 0$ and each free node's voltage is a weighted average of its neighbours' voltages (weights = conductances). An average can't exceed its largest input, so nothing beats the source (the discrete maximum principle; Doyle & Snell 1984). Measured: highest free node $= 1 + 8\times10^{-14}$ V for a 1 V source, i.e. 1 up to rounding.

So a passive network can only average, attenuate and split. It can never amplify.

## The op-amp is one row with no mirror

Model the op-amp as what it is electrically: a box whose output voltage is a huge number $A$ times the difference of its two inputs, $v_{out} = A(v_+ - v_-)$. In the matrix this is one new row containing $+A$ and $-A$ in the input columns, **with nothing at the mirrored positions**. The output doesn't load the inputs. Measured: $\max|M - M^T| = 10^5$, which is $A$.

That asymmetric entry is the whole device. It is what lets a node leave the convex hull of its neighbours. Inverting amplifier, $R_{in} = 1\,\text{k}\Omega$, $R_f = 10\,\text{k}\Omega$:

| open-loop gain $A$ | closed-loop gain | error vs $-10$ |
|---|---|---|
| 10 | −4.76 | 5.2 |
| 10³ | −9.891 | 0.11 |
| 10⁵ | −9.99890 | 1.1×10⁻³ |
| 10⁷ | −9.9999989 | 1.1×10⁻⁵ |

Formula: gain $= -\frac{R_f/R_{in}}{1 + (1 + R_f/R_{in})/A}$; the script matches it to every printed digit. As $A\to\infty$ the gain becomes $-R_f/R_{in}$, **set by two resistors and independent of the op-amp**. That is the point of negative feedback: you trade a large, sloppy number ($A$ varies 2× between parts and with temperature) for a ratio of resistors you can buy at 0.1%. "The inputs are equal" is just $v_+ - v_- = v_{out}/A \to 0$.

## The extra power has a channel

Load power 100 mW from a 1 mW input is not free. Accounting with ±15 V rails, 1 V in, 1 kΩ load:

- the −15 V supply rail delivers **165 mW**
- = load 100 mW + feedback resistor 10 mW + heat in the output transistor 55 mW.

The op-amp doesn't create energy; it is a valve. The input signal sets the valve, the rail supplies the flow. In matrix terms, the asymmetric row hides a current source fed from outside the network, which is why the averaging argument no longer applies.

## Carver Mead's version: the transistor, not the box

Mead's *Analog VLSI and Neural Systems* (1989, ch. 5) builds the amplifier from the physics up. The input stage is a **differential pair**: two transistors sharing a fixed bias current $I_b$. In subthreshold, transistor current is exponential in gate voltage, so the split is a hyperbolic tangent:

$$I_{out} = I_b \tanh\!\left(\frac{\kappa\,\Delta V}{2U_T}\right)$$

with $U_T = kT/q = 25.85$ mV (thermal voltage) and $\kappa \approx 0.7$ (how strongly the gate controls the channel). Measured: the open-loop stage is within 1% of a straight line only for $|\Delta V| < 12.8$ mV. Wire the same device as a follower (output fed back to the minus input), with small-signal gain 677: over **0 to 2 V** its deviation from a straight line is $2\times10^{-7}$ of the span, and the tracking error is $V_{in}/(1+A)$ = 2.95 mV at 2 V, measured and predicted. Feedback keeps the transistor parked in its 13 mV linear window while the output swings volts.

## Time: gain × bandwidth is fixed

A real op-amp has one deliberately slow internal pole (here 10 Hz, $A_0 = 10^5$, so gain-bandwidth product GBW = 1 MHz). Solve the same matrix at each frequency with $A(f) = A_0/(1 + jf/f_p)$:

| closed-loop gain | −3 dB bandwidth | GBW / (1 + R_f/R_in) |
|---|---|---|
| 1 | 500.01 kHz | 500.00 kHz |
| 10 | 90.92 kHz | 90.91 kHz |
| 100 | 9.91 kHz | 9.90 kHz |

Ask for 10× more gain, get 10× less bandwidth.

## The matrix solves circuits that cannot exist

Swap the op-amp's two inputs (positive feedback). The matrix still solves: output $-1.0001$ V. Simulate it in time and the output runs to the +15 V rail. The pole that was at $-5.7\times10^5$ s⁻¹ (decay) is now at $+5.7\times10^5$ s⁻¹ (growth). **A balance is not a stable state.** $Gv = i$ says where the forces cancel; whether the circuit stays there is a separate question about the eigenvalues of the dynamics.

## Where this stops working

- **The node voltage is only a potential when the circuit is small.** In the full theory the field is described by the four-potential $(\phi, \mathbf A)$, and $\mathbf E = -\nabla\phi - \partial\mathbf A/\partial t$. Circuit theory keeps $\phi$ (the node voltage) and confines $\partial\mathbf A/\partial t$ to the inductors. That holds when the board is much smaller than the wavelength: a 10 cm board is 3×10⁻⁴ wavelengths at 1 MHz (fine) and 0.33 at 1 GHz (it is now an antenna, and you need transmission lines). Mead's *Collective Electrodynamics* (2000) rebuilds electromagnetism directly from the four-potential; the lumped matrix is its slow, small-scale limit.
- **The one-pole model hides instability with capacitive loads.** Real op-amps have a second pole; a capacitor on the output adds a third, and the "stable" negative-feedback circuit can oscillate. That is the next experiment (phase margin).

*This is wrong if* some resistor-only network produces a free node above its source by more than rounding, or the closed-loop gain depends on $A$ more strongly than $(1 + R_f/R_{in})/A$.
