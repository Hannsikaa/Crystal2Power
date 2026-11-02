import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx_helpers import set_cell_margins, set_cell_borders, format_table, add_footer_page_numbers

def build_proposal_doc(output_docx_path):
    doc = docx.Document()

    # Page Setup: Standard A4 / Letter, 1 inch margins
    for s in doc.sections:
        s.page_width = Inches(8.5)
        s.page_height = Inches(11.0)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        s.different_first_page_header_footer = False

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # Document Header / Title Block (NO cover page, NO decorative images)
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.line_spacing = 1.15
    run_t = p_title.add_run("INTELLIGENT FLOOD WATER ELECTRIFICATION RISK PREDICTION AND AUTOMATIC ELECTRICAL ISOLATION FOR CLIMATE RESILIENT COMMUNITIES")
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(12.5)
    run_t.font.bold = True

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(2)
    p_meta.paragraph_format.space_after = Pt(14)
    p_meta.paragraph_format.line_spacing = 1.1
    run_meta = p_meta.add_run(
        "Technical and Project Details Proposal | ANRF – Inclusivity Research Grant (IRG)\n"
        "Principal Investigator: Dr. Dhanalakshmi Banavath, Assistant Professor, Department of Electronics and Communication Engineering\n"
        "Project Duration: Three Years (36 Months) | Proposed Collaboration: ECE Department Only | Co-PI: None"
    )
    run_meta.font.name = 'Times New Roman'
    run_meta.font.size = Pt(9.5)
    run_meta.font.italic = True

    # Helper functions for adding content
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.bold = True
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.12
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        return p

    def add_eq(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.italic = True
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.12
        run_b = p.add_run(bold_prefix)
        run_b.font.name = 'Times New Roman'
        run_b.font.size = Pt(10.5)
        run_b.font.bold = True
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(10.5)
        return p

    # =========================================================================
    # SECTION 1
    # =========================================================================
    add_h1("1. Origin of the Proposal and Rationale")

    add_p(
        "Severe flood events represent one of the most recurring and devastating manifestations of global climate change, "
        "imposing escalating humanitarian, economic, and infrastructural burdens across urban settlements, rural communities, "
        "and industrial zones. While contemporary flood mitigation initiatives predominantly focus on civil flood defenses, "
        "hydrological modelling, and mass evacuations, an acute secondary hazard that frequently leads to severe injuries, "
        "cardiac arrest, and fatalities is flood-related electrical hazards. As inundation encroaches upon built environments, "
        "floodwater penetrates residential buildings, low-lying public healthcare centers, schools, and community facilities. "
        "In doing so, the conductive fluid comes into direct physical contact with compromised electrical installations, "
        "including baseboard distribution wiring, junction boxes, submerged consumer electronics, service entry terminals, "
        "and building switchboards (FEMA P-348, 2017). Because municipal and river floodwaters carry substantial dissolved minerals, "
        "suspended solids, and ionic contaminants, their bulk electrical conductivity is elevated by orders of magnitude relative to "
        "pure water. Consequently, when energized conductors are submerged or splashed, high-magnitude fault currents and conductive "
        "voltage gradients disperse rapidly throughout the standing body of water."
    )

    add_p(
        "This electrification of floodwater poses fatal risks to both trapped residents attempting self-evacuation and rescue personnel "
        "operating inflatable rafts or wading on foot. Human physiological susceptibility to low-frequency alternating currents (50 Hz / 60 Hz) "
        "is exceptionally high; contact with body-accessible step-and-touch potentials as low as 50 V RMS under wet, uninsulated conditions "
        "exceeds safe thresholds specified in international electrical safety standards (IEC 60364-4-41, 2017). Currents passing through "
        "the human myocardium can readily induce ventricular fibrillation, respiratory tetanus, and drowning due to loss of motor control. "
        "Furthermore, persistent arcing and short-circuit faults in submerged wiring conduits routinely ignite structural fires in "
        "inundated structures where traditional fire suppression access is completely paralyzed."
    )

    add_p(
        "Conventional approaches to building electrical safety under flood conditions rely either on manual mains disconnection by "
        "occupants or utility-level distribution feeder cut-offs. Manual isolation is fraught with severe life-safety risks: residents "
        "are often absent during rapid flash floods, immobilized, or forced to traverse energized standing water to reach service panels, "
        "resulting in direct contact electrocution. Conversely, wide-area feeder tripping by utility distribution operators de-energizes "
        "entire neighborhoods indiscriminately, disabling vital municipal assets such as emergency stormwater sump pumps, communication "
        "repeaters, ventilator power in local healthcare clinics, and street illumination essential for navigation. While localized automated "
        "monitoring systems utilizing discrete water-level threshold triggers have emerged in literature, standard threshold-based methods "
        "suffer from severe operational limitations. In realistic flood environments, simple liquid-level switches and fixed-height ultrasonic "
        "sensors are plagued by high-frequency measurement noise caused by water turbulence, splashing, and floating debris; long-term calibration "
        "drift; sensor fouling; intermittent data dropouts; stuck-at readings; and cross-sensor contradictions (Ni et al., 2009; Sharma et al., 2010). "
        "A rigid threshold logic lacks the intelligence to differentiate between temporary harmless splashing and sustained structural inundation, "
        "resulting in premature nuisance tripping that shuts down life-critical pumps, or worse, catastrophic failure to isolate when hazardous "
        "energization occurs before a static water threshold is crossed."
    )

    add_p(
        "Consequently, there is an imperative scientific rationale to formulate and evaluate an intelligent, sensor-health-aware monitoring "
        "and decision framework. By synthesizing embedded multi-sensor telemetry, online sensor fault diagnosis, computational electrical hazard "
        "modelling, and evidential reasoning under uncertainty, the proposed research aims to establish a dependable safety-oriented architecture "
        "capable of timely, controlled low-voltage isolation while rigorously minimizing false alarms and missed hazards."
    )

    # =========================================================================
    # SECTION 2
    # =========================================================================
    add_h1("2. National and International Status of Research")

    add_p(
        "The technological landscape encompassing environmental flood monitoring, sensor network dependability, and electrical infrastructure "
        "safety spans multiple interconnected disciplines in engineering and computer science."
    )

    add_p(
        "International Research Status: In the domain of flood monitoring and early warning, networked embedded sensing has evolved from "
        "sparse hydrometric gauging stations to dense Internet of Things (IoT) deployments. Foundational investigations by Basha et al. (2008) "
        "demonstrated model-based wireless sensor networks for river-basin flood forecasting, establishing that predictive physical modelling "
        "substantially enhances early-warning lead time. Contemporary municipal initiatives, such as the FloodNet project deployed across "
        "New York City (Mydlarz et al., 2024), demonstrate the feasibility of hyper-local street-level inundation tracking using low-cost "
        "ultrasonic rangefinders and edge telemetry. However, these systems are exclusively configured for urban hydrology and municipal transit "
        "alerting; they do not monitor built electrical infrastructure nor interface with electrical protection mechanisms. In the realm of "
        "automated electrical isolation, researchers have explored coupling water-level sensors with smart switchgear (Lo and Ansari, 2012). "
        "Small-scale automated disconnection prototypes have been reported in literature (Depari et al., 2020), utilizing microcontrollers to "
        "trip miniature circuit breakers (MCBs) via motorized servos or electromechanical relays upon detecting liquid ingress. However, these "
        "demonstrations uniformly rely on unvalidated, deterministic single-sensor threshold rules. They omit sensor-health assessment, treating "
        "every transducer reading as inherently ground truth, thereby exposing the system to catastrophic false tripping or missed isolation "
        "during sensor failures."
    )

    add_p(
        "In the domain of sensor network dependability and fault diagnosis, international literature provides extensive theoretical foundations. "
        "Ni et al. (2009) established a comprehensive data-centric taxonomy of sensor faults in physical deployments, categorizing anomalies into "
        "additive offsets, gain degradation, gradual drift, stuck-at-constant states, and high-frequency noise bursts. Sharma et al. (2010) "
        "evaluated the prevalence of these failure modes across real-world environmental sensor datasets, highlighting that transient and permanent "
        "sensor abnormalities occur regularly under harsh climatic exposure. Survey works by Zhang et al. (2010) categorized outlier and anomaly "
        "detection paradigms into rule-based, parametric statistical, nearest-neighbor, and spectral methods. Furthermore, to address decision-making "
        "under sensor degradation, multi-sensor data fusion frameworks based on Dempster-Shafer theory of evidence (Dempster, 1967; Shafer, 1976) "
        "and generalized probabilistic fusion (Hall and Llinas, 1997; Castanedo, 2013) have been successfully investigated in robotics and aerospace. "
        "Similarly, international functional safety standards, notably IEC 61508-1 (2010) and ISO 13849-1 (2015), mandate systematic fault detection, "
        "safe state transitions, and diagnostic coverage in safety-related embedded control architectures."
    )

    add_p(
        "National Research Status: Within India, national regulatory guidelines and technical building codes stipulate baseline requirements for "
        "electrical safety in moisture-prone installations. The National Building Code of India (NBC 2016, BIS) and the Central Electricity "
        "Authority (Measures relating to Safety and Electric Supply) Regulations (CEA, 2010) prescribe the mandatory inclusion of Residual Current "
        "Devices (RCDs) with a 30 mA tripping sensitivity, equipotential earthing, and minimum Ingress Protection (IP) enclosures for installations "
        "exposed to weather. In addition, the National Disaster Management Authority (NDMA, 2010) Urban Flooding Guidelines emphasize the vulnerability "
        "of municipal power distribution grids during severe monsoon inundations. In academic research, Indian investigators have contributed "
        "notably to sensor fault diagnosis and distributed network resilience. Mahapatro and Khilar (2013) presented an exhaustive survey of fault "
        "diagnosis techniques in wireless sensor networks, outlining cluster-based, localized, and residual-checking algorithms. Indian academic "
        "groups have also developed localized urban flood forecasting systems utilizing rainfall telemetry and hydrological run-off modelling."
    )

    add_p(
        "However, a critical review of the national and international literature reveals that research explicitly coupling online sensor-health "
        "diagnostics with computational electrical hazard estimation and automated isolation remains highly scarce. Existing research predominantly "
        "bifurcates into either purely hydrological flood warning systems or isolated electrical switchgear studies lacking real-time environmental "
        "intelligence. The national research literature has not yet addressed the integration of uncertainty-aware embedded reasoning to govern "
        "pre-emptive, safety-oriented electrical isolation during structural flooding."
    )

    # =========================================================================
    # SECTION 3
    # =========================================================================
    add_h1("3. Research Gap and Proposed Novelty")

    add_p(
        "Despite significant advancements in IoT sensing and automated switchgear, critical technical gaps persist at the intersection of "
        "flood telemetry and electrical hazard mitigation:"
    )

    add_bullet(
        "Gap 1: Absence of Sensor-Health Verification in Hazard Decision-Making. ",
        "Prior flood-triggered electrical isolation systems operate on raw transducer outputs, assuming perfect sensor fidelity. In practical "
        "flood scenarios, sensors are exposed to acoustic echoes, splashing, suspended silt, corrosion, and physical displacement. The literature "
        "lacks an embedded fault diagnosis mechanism capable of detecting noise, calibration drift, stuck-at values, and cross-channel contradictions "
        "prior to hazard computation."
    )
    add_bullet(
        "Gap 2: Lack of Coupled Hydrodynamic and Electrical Hazard Modelling. ",
        "Conventional threshold devices presume that electrical danger is a monotonic, deterministic function of static water depth. In reality, "
        "the physical inception of electrical hazards depends dynamically on water ingress rate, fluid electrical conductivity, insulation resistance "
        "degradation of immersed conductors, and circuit topology. Existing literature lacks computationally efficient, lumped-parameter models "
        "suitable for real-time execution on low-power microcontrollers."
    )
    add_bullet(
        "Gap 3: Deterministic Binary Triggering under Measurement Uncertainty. ",
        "Existing systems enforce crisp, binary switching (tripping power immediately upon crossing a hard depth threshold). When measurements are "
        "ambiguous, noisy, or conflicting, deterministic logic produces high rates of false alarms (unwarranted blackouts of emergency pumps) "
        "or catastrophic false negatives. There is a marked absence of evidential reasoning architectures that quantify uncertainty and bound "
        "belief before asserting safety-critical control actions."
    )
    add_bullet(
        "Gap 4: Absence of Multi-Tiered Fail-Safe State Progression. ",
        "Current prototypes switch abruptly between fully energized and tripped states, lacking intermediate advisory, warning, and sensor-fault "
        "fallback modes mandated by functional safety engineering principles."
    )

    add_p(
        "To address these identified gaps, the candidate novelties of this research project include:"
    )
    add_bullet(
        "Candidate Novelty 1: Online Embedded Sensor-Health Diagnostics for Flood Transducers. ",
        "Formulating and embedding a lightweight, multi-stage data-quality assessment pipeline executing real-time range plausibility, rate-of-change "
        "gradient filtering, rolling variance profiling, and cross-sensor residual checking to assign dynamic Sensor Health Indices (SHI) to all inputs."
    )
    add_bullet(
        "Candidate Novelty 2: Uncertainty-Aware Evidential Hazard Estimation. ",
        "Formulating an evidential reasoning framework (adapting Dempster-Shafer theory with SHI-discounted basic probability assignments) that "
        "synthesizes multi-sensor flood observations with computational electrical hazard models to yield bounded Hazard Indices (HI) under incomplete "
        "or conflicting telemetry."
    )
    add_bullet(
        "Candidate Novelty 3: Safety-Oriented Multi-Tiered Decision Logic with Deterministic Fail-Safe Fallbacks. ",
        "Designing a finite state machine that navigates discrete operational states (Normal Monitoring, Advisory Warning, Urgent Warning, "
        "Controlled Isolation, and Degraded Sensor Fault State), ensuring deterministic protection and preventing premature de-energization of "
        "emergency loads."
    )
    add_bullet(
        "Candidate Novelty 4: Rigorous Empirical Benchmarking on a Protected Low-Voltage Demonstrator. ",
        "Executing systematic synthetic fault injection and physical bench testing on a safe, isolated, current-limited experimental apparatus "
        "to quantitatively establish sensitivity, specificity, false-alarm reduction, and decision latency against traditional threshold-based systems."
    )

    # =========================================================================
    # SECTION 4
    # =========================================================================
    add_h1("4. Research Aim and Questions")

    add_p(
        "The overarching aim of this research project is to formulate, implement, computationally evaluate, and experimentally validate "
        "an intelligent, sensor-health-aware embedded monitoring and decision framework capable of predicting flood-related electrical hazards "
        "and executing controlled electrical isolation within a protected low-voltage laboratory environment."
    )

    add_p(
        "To achieve this overarching aim, the investigation is directed by four focused research questions:"
    )
    add_bullet(
        "Research Question 1 (RQ1): ",
        "To what extent does the incorporation of real-time sensor fault diagnosis (identifying noise, drift, stuck-at values, and cross-sensor "
        "inconsistencies) improve the reliability and accuracy of flood hazard estimation compared to conventional unvalidated threshold methods?"
    )
    add_bullet(
        "Research Question 2 (RQ2): ",
        "How can computational electrical hazard modelling and evidential reasoning under measurement uncertainty effectively synthesize degraded, "
        "missing, or contradictory multi-sensor observations without falsely declaring an energized environment to be safe?"
    )
    add_bullet(
        "Research Question 3 (RQ3): ",
        "What multi-tiered decision logic and state-transition criteria optimally balance the prevention of human electrocution hazards against the "
        "operational necessity of avoiding nuisance power disconnections for critical emergency infrastructure?"
    )
    add_bullet(
        "Research Question 4 (RQ4): ",
        "Can the formulated diagnostic, estimation, and decision algorithms execute deterministically within the strict computational, memory, "
        "and latency constraints of a resource-bounded 32-bit embedded microcontroller platform?"
    )

    # =========================================================================
    # SECTION 5
    # =========================================================================
    add_h1("5. Research Methodology")

    add_p(
        "The research methodology follows a rigorous, simulation-first engineering lifecycle, progressing from mathematical formulation and "
        "computational simulation to safe hardware-in-the-loop firmware development and controlled laboratory validation on an isolated, "
        "current-limited low-voltage apparatus. The technical methodology is organized into eight sequential subsections."
    )

    add_h2("5.1 Literature Review and Problem Formulation")
    add_p(
        "The initial phase establishes a rigorous theoretical foundation through a systematic survey of peer-reviewed literature, patents, "
        "and international safety standards governing flood telemetry, sensor fault diagnosis, and electrical safety installations. The operating "
        "domain is formalized into measurable state variables, mathematical boundaries, and environmental constraints. Let the physical environment "
        "be characterized at discrete time step k by the state vector x_k = [h(k), ḣ(k), T(k), RH(k), R_ins(k), I_leak(k)]^T, where h(k) denotes water depth, "
        "ḣ(k) represents inundation rate (dh/dt), T(k) is ambient temperature, RH(k) is relative humidity, R_ins(k) is insulation resistance of low-voltage target "
        "wiring, and I_leak(k) is circuit leakage current. The system boundary stipulates a protected low-voltage indoor environment (V_op ≤ 24 V DC / 24 V AC, "
        "current limited to ≤ 2 A). Functional safety targets are defined in alignment with IEC 61508-1 (2010): maximum decision latency t_lat < 500 ms, "
        "false-negative hazard rate ≤ 0.1%, and verifiable fail-safe default behavior under total sensor loss."
    )

    add_h2("5.2 Scenario Definition and Computational Modelling")
    add_p(
        "Representative flood and fault scenarios are formalized to evaluate system robustness across diverse operating conditions. Inundation profiles "
        "are categorized into three distinct regimes: (a) slow cumulative seepage (0.1 cm/min ≤ ḣ ≤ 1.0 cm/min), (b) rapid flash ingress (10 cm/min ≤ ḣ ≤ 50 cm/min), "
        "and (c) turbulent splashing with surface wave dynamics. The computational electrical hazard model couples liquid ingress dynamics with lumped-parameter "
        "electrical circuit equations. As conductive water bridges electrical conductors separated by distance d, the equivalent shunt resistance R_path "
        "of the aqueous path is modelled as:"
    )
    add_eq("R_path(k) = (1 / σ_water) · [d / A_eff(h(k))]")
    add_p(
        "where σ_water represents fluid bulk electrical conductivity (ranging from 0.005 S/m for rainwater to 0.05 S/m for mineralized runoff), "
        "and A_eff(h(k)) represents the effective contact cross-sectional area as a function of instantaneous water depth h(k). "
        "Simultaneously, insulation degradation under extreme ambient humidity and partial wetting is modelled via exponential decay: "
        "R_ins(k) = R_0 · exp(-α · RH(k) · t). The model outputs continuous leakage current I_leak(k) = V_op / [R_path(k) + R_ins(k)] "
        "and contact hazard risk. Crucially, the model incorporates explicit assumptions: isothermal fluid properties over short windows, linear field "
        "distribution, and bounded maximum ionic concentrations. Sensor fault injection models are mathematically integrated, introducing additive Gaussian "
        "noise w(k) ~ N(0, σ²), linear calibration drift d(k) = β · k, stuck-at-constant faults y(k) = y_stuck, and probabilistic packet loss P(loss) = γ."
    )

    add_h2("5.3 Sensor Selection and Data Acquisition")
    add_p(
        "To ensure robust environmental perception in the low-voltage laboratory prototype, a diverse multi-modal sensing strategy is formulated, "
        "combining non-contact and contact physical transducers with circuit state monitoring:"
    )
    add_bullet(
        "Water Level and Presence Sensing: ",
        "A dual-channel approach utilizing an ultrasonic time-of-flight distance transducer (non-contact rangefinder positioned above the fluid surface, "
        "providing continuous depth h_us(k)) coupled with a multi-point resistive/hydrostatic pressure level sensor submerged at the container base "
        "(h_res(k)). This physical diversity prevents common-mode sensing failures such as surface foam scattering or floating debris obstruction."
    )
    add_bullet(
        "Environmental Condition Monitoring: ",
        "Integrated digital temperature and relative humidity sensing modules to track condensation, ambient moisture saturation, and provide "
        "temperature compensation for ultrasonic speed-of-sound corrections: v_sound = 331.3 · √(1 + T / 273.15) m/s."
    )
    add_bullet(
        "Low-Voltage Circuit State Telemetry: ",
        "High-precision, galvanically isolated current-shunt monitors and differential voltage dividers interfaced with the low-voltage test load, "
        "providing real-time telemetry of load voltage V_load(k) and leakage/fault current I_leak(k) without physical electrical connection "
        "to the microcontroller core."
    )
    add_p(
        "The data acquisition pipeline executes deterministic synchronous sampling at f_s = 20 Hz governed by a hardware timer interrupt. "
        "Analog sensor signals undergo first-order RC anti-aliasing filtering, 12-bit ADC digitization, and circular ring-buffering. Telemetry packets "
        "are strictly time-stamped with microsecond precision, verified via cyclic redundancy checks (CRC-16), and queued for online validation."
    )

    add_h2("5.4 Sensor Fault Diagnosis and Data-Quality Assessment")
    add_p(
        "The sensor fault diagnosis module executes an online, lightweight, four-stage validation pipeline designed for deterministic execution "
        "within embedded microprocessor cycles without floating-point bottlenecks (Ni et al., 2009; Mahapatro and Khilar, 2013):"
    )
    add_bullet(
        "Stage 1: Physical Boundary and Plausibility Checks. ",
        "Each raw reading y_i(k) is verified against physical geometry limits: y_i,min ≤ y_i(k) ≤ y_i,max. Out-of-bounds readings "
        "(e.g., negative distances or depths exceeding test tank height) immediately trigger an anomaly flag."
    )
    add_bullet(
        "Stage 2: Dynamic Gradient and Rate-of-Change Constraints. ",
        "The discrete temporal derivative is evaluated: Δy_i(k) = |y_i(k) - y_i(k-1)| / Δt. Inundation rates exceeding physically "
        "attainable hydrological limits ḣ_max indicate acoustic reflection glitches, EMI spikes, or mechanical shock rather than true water movement."
    )
    add_bullet(
        "Stage 3: Rolling Statistical Variance and Stuck-at Detection. ",
        "Over a sliding window of W = 20 samples, the sample variance σ_i²(k) is monitored. If σ_i²(k) < ε_noise while the system is in a dynamic "
        "state, a stuck-at fault is flagged. Conversely, if σ_i²(k) > θ_noise, a high-frequency noise anomaly is diagnosed."
    )
    add_bullet(
        "Stage 4: Heterogeneous Cross-Sensor Residual Analysis. ",
        "The spatial residual between independent physical sensors measuring equivalent phenomena is computed: r_12(k) = |h_us(k) - h_res(k)|. "
        "Under normal conditions, r_12(k) ≤ δ_thresh. Persistent divergence indicates calibration drift, transducer fouling, or partial detachment."
    )
    add_p(
        "The diagnostic engine compiles these checks into a normalized continuous Sensor Health Index SHI_i(k) ∈ [0.0, 1.0] for each transducer i:"
    )
    add_eq("SHI_i(k) = ∏ [ω_j · φ_i,j(k)]   (for j = 1 to 4)")
    add_p(
        "where φ_i,j(k) ∈ [0, 1] represents the verification score for diagnostic stage j, and ω_j are stage importance weights. "
        "A healthy sensor exhibits SHI_i ≥ 0.85, while degraded or faulty sensors drop below 0.50."
    )

    add_h2("5.5 Hazard Estimation under Uncertainty")
    add_p(
        "Hazard estimation under measurement uncertainty is formulated via evidential reasoning, adapting the Dempster-Shafer theory of evidence "
        "(Shafer, 1976; Castanedo, 2013). Let the frame of discernment be Ω = {H, ¬H}, denoting the proposition that an electrical hazard "
        "is physically imminent/present (H) or absent (¬H). Rather than relying on rigid binary thresholds, each sensor channel i generates a "
        "basic probability assignment (BPA) or mass function m_i(·) derived from its physical measurement relative to the computational hazard model. "
        "Crucially, the raw belief mass is discounted by its instantaneous sensor health index SHI_i(k):"
    )
    add_eq("m_i(H) = SHI_i(k) · f_model(y_i(k)),   m_i(¬H) = SHI_i(k) · [1 - f_model(y_i(k))],   m_i(Ω) = 1 - SHI_i(k)")
    add_p(
        "where m_i(Ω) represents the uncommitted epistemic uncertainty. Evidence from the diverse sensing channels is combined using Dempster's rule "
        "of combination. For two independent sources with conflict metric K = ∑_{A ∩ B = ∅} m_1(A) · m_2(B):"
    )
    add_eq("m_12(A) = [1 / (1 - K)] · ∑_{B ∩ C = A} m_1(B) · m_2(C),   ∀ A ⊆ Ω, A ≠ ∅")
    add_p(
        "The fused mass function yields a lower bound of belief Bel(H) = m(H) and an upper bound of plausibility Pl(H) = m(H) + m(Ω). "
        "The composite Hazard Index is evaluated as HI(k) = [Bel(H) + Pl(H)] / 2. This formulation guarantees that if sensor health degrades "
        "(SHI → 0), uncertainty m(Ω) → 1; the system recognizes its own ignorance rather than falsely declaring that the installation is safe."
    )

    add_h2("5.6 Safety-Oriented Decision-Making and Electrical Isolation")
    add_p(
        "The decision-making architecture employs a deterministic, finite state machine (FSM) designed in accordance with functional safety principles "
        "(IEC 61508-1, 2010; ISO 13849-1, 2015). The controller navigates five distinct operational states:"
    )
    add_bullet(
        "State 0 (Normal Monitoring): ",
        "HI(k) < 0.30 and overall average sensor health SHI_avg ≥ 0.80. The low-voltage circuit remains fully energized; normal telemetry "
        "and periodic diagnostic self-checks are logged."
    )
    add_bullet(
        "State 1 (Advisory Warning): ",
        "0.30 ≤ HI(k) < 0.60. Water ingress is detected at low elevations, but clearance to electrical conductors remains substantial. "
        "Flashing amber visual indicators and auditory alert chimes are activated. Power is maintained to ensure uninterrupted operation of auxiliary equipment."
    )
    add_bullet(
        "State 2 (Urgent Warning): ",
        "0.60 ≤ HI(k) < 0.80. Rapid water rise or insulation resistance degradation indicates imminent encroachment within a 60-second horizon. "
        "Rapid pulsing alerts are triggered; local telemetry is pushed to the logging buffer."
    )
    add_bullet(
        "State 3 (Controlled Isolation Command): ",
        "HI(k) ≥ 0.80. Electrical hazard condition is verified. The controller de-energizes the pilot circuit of a fast-acting isolation contactor "
        "within ≤ 20 ms. Power to the protected low-voltage circuit is severed. Re-energization requires a deliberate physical manual reset."
    )
    add_bullet(
        "State 4 (Degraded / Sensor Fault State): ",
        "Triggered when persistent sensor faults or unresolvable cross-sensor contradictions cause m(Ω) > 0.60 or SHI_avg < 0.50. "
        "A dedicated fault code is broadcast. If secondary parameters (e.g., humidity or pressure) indicate wet conditions, a conservative, "
        "timed fail-safe isolation countdown is initiated, preventing unmonitored electrification."
    )

    add_h2("5.7 Embedded Prototype Development")
    add_p(
        "The physical demonstrator is engineered strictly as a protected, bench-scale low-voltage laboratory apparatus. The embedded processing "
        "core comprises a 32-bit ARM Cortex-M4 microcontroller operating at 168 MHz with integrated floating-point hardware and hardware watchdog timers. "
        "All sensor inputs are routed through optocoupled galvanic isolation barriers to prevent noise coupling. The low-voltage switching assembly "
        "integrates a solid-state relay (SSR) and a redundant electromechanical safety contactor configured in an 'energize-to-close / de-energize-to-open' "
        "fail-safe topology. The demonstrator powers a low-voltage DC/AC bench test circuit (12 V / 24 V, max 2 A) with resistive and inductive loads, "
        "powered exclusively by a current-limited, isolated bench power supply. The assembly is housed within a clear, shatterproof polycarbonate "
        "enclosure rated to IP65, equipped with mechanical safety interlocks, an external emergency stop switch, and an onboard micro-SD datalogger "
        "capturing raw telemetry, diagnostic flags, and state transitions at 20 Hz."
    )

    add_h2("5.8 Laboratory Validation and Performance Evaluation")
    add_p(
        "Controlled laboratory validation is executed in a dedicated, sealed fluid test chamber. Water levels, ingress rates, and fluid conductivity "
        "are accurately regulated using a peristaltic metering pump and closed-loop reservoir. The evaluation protocol encompasses three comprehensive "
        "experimental test regimes:"
    )
    add_bullet(
        "Regime A: Baseline Hydrological and Dynamic Flood Profiles. ",
        "Testing slow filling, rapid surging, and turbulent surface sloshing to evaluate standard detection accuracy and response timing."
    )
    add_bullet(
        "Regime B: Synthetic Fault Injection and Stress Testing. ",
        "Systematic software and hardware fault injection: inserting additive Gaussian noise, calibration drift slopes (0.5 cm/min), "
        "stuck-at-zero/stuck-at-max values, partial sensor masking (simulating mud fouling), and 10% to 50% burst packet loss."
    )
    add_bullet(
        "Regime C: Power Interruption and Transient Disturbance. ",
        "Simulating supply brownouts, transient voltage spikes, and abrupt power restoration to verify state recovery without unintended re-energization."
    )
    add_p(
        "The proposed framework is benchmarked directly against a conventional fixed-threshold system. Quantitative evaluation criteria comprise: "
        "(a) Classification Performance: Sensitivity (Recall), Specificity, Precision, and F1-score across 500 simulated and experimental trials; "
        "(b) Safety and Dependability: False Alarm Rate (FAR) and Missed Hazard Rate (MHR); (c) Temporal Dynamics: Mean diagnostic detection latency (t_diag) "
        "and total electrical isolation time (t_iso); and (d) Computational Footprint: Microcontroller CPU load percentage, RAM utilization, and "
        "execution jitter across real-time scheduling loops."
    )

    # =========================================================================
    # SECTION 6
    # =========================================================================
    add_h1("6. Conceptual System Description")

    add_p(
        "The conceptual system architecture translates multi-modal physical observations into deterministic, safety-oriented control actions "
        "through a structured, modular pipeline. As mandated by project safety and formatting boundaries, the functional organization is "
        "represented below in tabular form without graphical diagrams or flowcharts."
    )

    p_tbl1_caption = doc.add_paragraph()
    p_tbl1_caption.paragraph_format.space_before = Pt(6)
    p_tbl1_caption.paragraph_format.space_after = Pt(2)
    p_tbl1_caption.paragraph_format.keep_with_next = True
    run_c1 = p_tbl1_caption.add_run("Table 1: Functional Block Architecture of the Proposed Framework")
    run_c1.font.bold = True
    run_c1.font.size = Pt(10)

    t1_headers = ["Functional Block", "Primary Purpose and Operations", "Main Outputs Produced"]
    t1_data = [
        [
            "1. Sensing and Data Acquisition Block",
            "Samples non-contact ultrasonic distance, submerged resistive level, ambient temperature, relative humidity, and isolated low-voltage load telemetry via 12-bit ADC at 20 Hz synchronous intervals.",
            "Synchronized, timestamped, CRC-verified raw telemetry vector x_k."
        ],
        [
            "2. Sensor-Health Diagnosis Block",
            "Executes real-time physical plausibility checks, rate-of-change gradient filtering, sliding-window variance profiling, and cross-sensor residual monitoring.",
            "Sensor Health Indices (SHI_i in [0, 1]) and discrete fault classification flags."
        ],
        [
            "3. Computational Hazard Modelling Block",
            "Computes dynamic water ingress rates, aqueous path resistance, insulation degradation, and theoretical electrical leakage parameters.",
            "Model-derived physical electrical hazard probabilities f_model(x_k)."
        ],
        [
            "4. Uncertainty-Aware Fusion Block",
            "Discounts belief masses by SHI, synthesizes multi-channel evidence using Dempster-Shafer formulation, and bounds epistemic uncertainty.",
            "Composite Hazard Index HI(k) bounded by Belief Bel(H) and Plausibility Pl(H)."
        ],
        [
            "5. Safety Decision and FSM Block",
            "Evaluates multi-tiered threshold criteria against the 5-state finite state machine with deterministic fail-safe state transition rules.",
            "Active system operational state (Normal, Advisory, Urgent, Isolation, Fault State)."
        ],
        [
            "6. Controlled Low-Voltage Isolation Block",
            "Drives solid-state relays and electromechanical safety contactors to disconnect isolated bench power supply from protected test load.",
            "De-energization of low-voltage circuit (< 20 ms), visual/auditory alarms, interlock latch."
        ],
        [
            "7. Black-Box Logging and HMI Block",
            "Serializes high-resolution sensor telemetry, diagnostic health metrics, state changes, and actuation timestamps to non-volatile micro-SD storage.",
            "Structured CSV/binary event logs for post-test analysis and local OLED status display."
        ]
    ]
    t1_widths = [Inches(1.8), Inches(3.2), Inches(1.5)]
    table1 = doc.add_table(rows=len(t1_data) + 1, cols=3)
    format_table(table1, t1_widths, t1_headers, t1_data)

    # =========================================================================
    # SECTION 7
    # =========================================================================
    add_h1("7. Expected Technical Contribution")

    add_p(
        "This research project will advance the state of the art in embedded safety systems and environmental hazard mitigation. "
        "The expected contributions are categorized into three distinct domains:"
    )

    add_bullet(
        "1. Foundational Research Outputs and Scientific Algorithms: ",
        "The project will deliver: (a) a validated mathematical model coupling physical flood inundation dynamics with electrical insulation degradation "
        "and conductive fluid leakage currents; (b) an online, resource-efficient sensor fault diagnosis algorithm capable of detecting noise, calibration drift, "
        "stuck-at anomalies, and sensor disagreements on resource-constrained embedded targets; and (c) an evidential reasoning framework for uncertainty "
        "quantification that prevents false assertions of safety under degraded sensory conditions."
    )
    add_bullet(
        "2. Protected Low-Voltage Laboratory Demonstrator: ",
        "The hardware output consists of a fully integrated, galvanically isolated, current-limited laboratory prototype operating at safe voltage levels "
        "(≤ 24 V DC / 24 V AC, max 2 A). This physical demonstrator provides an empirical testbed demonstrating deterministic isolation latency under 20 ms, "
        "verifiable fail-safe latching, and black-box data logging."
    )
    add_bullet(
        "3. Methodological Insights and Future Translational Pathways: ",
        "The research will produce an open experimental dataset and comparative performance benchmark contrasting evidential decision frameworks "
        "against industry-standard threshold tripping. These technical insights will establish design guidelines for future industrial development "
        "of climate-resilient smart building distribution boards and municipal electrical safety standards."
    )

    # =========================================================================
    # SECTION 8
    # =========================================================================
    add_h1("8. Three-Year Work Plan")

    add_p(
        "The 36-month project execution is structured across three cohesive, sequential annual phases, maintaining a simulation-first methodology "
        "prior to hardware fabrication and laboratory testing."
    )

    p_tbl2_caption = doc.add_paragraph()
    p_tbl2_caption.paragraph_format.space_before = Pt(6)
    p_tbl2_caption.paragraph_format.space_after = Pt(2)
    p_tbl2_caption.paragraph_format.keep_with_next = True
    run_c2 = p_tbl2_caption.add_run("Table 2: Three-Year Detailed Work Plan")
    run_c2.font.bold = True
    run_c2.font.size = Pt(10)

    t2_headers = ["Project Phase", "Scheduled Technical Activities", "Expected Deliverables"]
    t2_data = [
        [
            "Year 1 (Months 1–12): Problem Formulation, Modelling, and Simulation",
            "• Comprehensive literature and patent analysis on flood telemetry and electrical hazards.\n"
            "• Formalization of mathematical state variables, environmental bounds, and safety requirements.\n"
            "• Development of coupled hydrodynamic and electrical hazard simulation models.\n"
            "• Formulation of synthetic sensor fault injection models (noise, drift, stuck-at, loss).\n"
            "• Simulation-based implementation of baseline threshold detection for benchmarking.\n"
            "• Selection and procurement of laboratory sensing, microcontroller, and safety components.",
            "• Comprehensive Technical Report on State-of-the-Art and System Architecture.\n"
            "• Validated MATLAB/Simulink Simulation Testbed.\n"
            "• Baseline Threshold Algorithm Benchmark Results.\n"
            "• Component Specifications and Procurement Dossier."
        ],
        [
            "Year 2 (Months 13–24): Algorithm Formulation and Embedded Prototype Design",
            "• Formulation of multi-stage online sensor fault diagnosis algorithms (SHI evaluation).\n"
            "• Formulation of evidential reasoning and Dempster-Shafer hazard estimation engine.\n"
            "• Design of 5-state finite state machine with fail-safe transition rules.\n"
            "• Extensive Monte Carlo simulation evaluating robustness across 1,000 fault scenarios.\n"
            "• Schematic capture, circuit simulation, and PCB design of isolated low-voltage demonstrator.\n"
            "• Firmware development for 32-bit MCU (deterministic ADC sampling, FreeRTOS/bare-metal loops).",
            "• Algorithmic Formulation and Simulation Report.\n"
            "• Complete Embedded Firmware Codebase (C/C++).\n"
            "• Fabricated and Verified Prototype Circuit Boards.\n"
            "• Peer-Reviewed Journal/Conference Manuscript on Algorithmic Framework."
        ],
        [
            "Year 3 (Months 25–36): Hardware Integration, Validation, and Dissemination",
            "• Assembly and bench integration of sensors, MCU board, and low-voltage switching assembly.\n"
            "• Construction of sealed fluid test chamber with controlled water circulation.\n"
            "• Execution of laboratory validation experiments across Regimes A, B, and C.\n"
            "• Empirical evaluation of sensitivity, specificity, false alarm rate, and isolation latency.\n"
            "• Comparative analysis of proposed system versus conventional threshold methods.\n"
            "• Compilation of final technical data, publication dissemination, and project closure.",
            "• Fully Functional, Protected Low-Voltage Laboratory Demonstrator.\n"
            "• Comprehensive Experimental Validation Dataset.\n"
            "• Second Peer-Reviewed Journal Publication in Reputed IEEE/Elsevier Venue.\n"
            "• Comprehensive Final Project Completion Report."
        ]
    ]
    t2_widths = [Inches(1.8), Inches(3.2), Inches(1.5)]
    table2 = doc.add_table(rows=len(t2_data) + 1, cols=3)
    format_table(table2, t2_widths, t2_headers, t2_data)

    # =========================================================================
    # SECTION 9
    # =========================================================================
    add_h1("9. Milestones and Deliverables")

    add_p(
        "Project progression is monitored against six verifiable milestones distributed across the 36-month timeline. "
        "Each milestone produces distinct, audit-ready deliverables."
    )

    p_tbl3_caption = doc.add_paragraph()
    p_tbl3_caption.paragraph_format.space_before = Pt(6)
    p_tbl3_caption.paragraph_format.space_after = Pt(2)
    p_tbl3_caption.paragraph_format.keep_with_next = True
    run_c3 = p_tbl3_caption.add_run("Table 3: Project Milestones and Verifiable Evidence of Completion")
    run_c3.font.bold = True
    run_c3.font.size = Pt(10)

    t3_headers = ["Milestone", "Target Month", "Technical Description", "Verifiable Evidence of Completion"]
    t3_data = [
        [
            "M1",
            "Month 6",
            "Completion of mathematical problem formulation, boundary limits, and baseline simulation.",
            "Detailed technical report and verified simulation scripts demonstrating coupled hazard models."
        ],
        [
            "M2",
            "Month 12",
            "Completion of sensor fault injection models and procurement of laboratory components.",
            "Simulation benchmark report against threshold models and verified component inventory."
        ],
        [
            "M3",
            "Month 18",
            "Formulation and simulation validation of sensor-health diagnosis and evidential fusion algorithms.",
            "Algorithmic design report and acceptance of peer-reviewed conference/journal paper."
        ],
        [
            "M4",
            "Month 24",
            "Completion of embedded firmware architecture and fabrication of isolated prototype PCB.",
            "Fabricated hardware PCB, firmware repository, and bench continuity test report."
        ],
        [
            "M5",
            "Month 30",
            "Commissioning of sealed fluid test chamber and execution of controlled laboratory trials.",
            "Demonstration of physical low-voltage prototype and verified experimental telemetry logs."
        ],
        [
            "M6",
            "Month 36",
            "Completion of comparative performance benchmarking, final reporting, and dissemination.",
            "Final comprehensive project report, published research manuscripts, and demonstration video."
        ]
    ]
    t3_widths = [Inches(0.9), Inches(1.1), Inches(2.7), Inches(1.8)]
    table3 = doc.add_table(rows=len(t3_data) + 1, cols=4)
    format_table(table3, t3_widths, t3_headers, t3_data)

    # =========================================================================
    # SECTION 10
    # =========================================================================
    add_h1("10. Risk Analysis and Mitigation")

    add_p(
        "A proactive risk management framework identifies potential technical, operational, and laboratory safety risks, "
        "establishing concrete mitigation strategies to ensure successful project execution."
    )

    p_tbl4_caption = doc.add_paragraph()
    p_tbl4_caption.paragraph_format.space_before = Pt(6)
    p_tbl4_caption.paragraph_format.space_after = Pt(2)
    p_tbl4_caption.paragraph_format.keep_with_next = True
    run_c4 = p_tbl4_caption.add_run("Table 4: Risk Analysis and Comprehensive Mitigation Matrix")
    run_c4.font.bold = True
    run_c4.font.size = Pt(10)

    t4_headers = ["Identified Risk", "Potential Effect on Project", "Proactive Mitigation Strategy"]
    t4_data = [
        [
            "1. Computational Overload on Microcontroller",
            "Algorithm execution exceeds real-time loop deadlines (50 ms), causing missed sampling frames.",
            "Optimize mathematics using fixed-point integer arithmetic; utilize look-up tables (LUTs); select 32-bit MCU with hardware FPU."
        ],
        [
            "2. Environmental Transducer Fouling",
            "Turbid floodwater deposits sediment on submerged probes, inducing persistent drift.",
            "Deploy heterogeneous sensing (non-contact ultrasonic + contact pressure); implement online drift detection to down-weight degraded channels."
        ],
        [
            "3. Premature Electrical Nuisance Tripping",
            "Inadvertent power shutoff during non-hazardous surface wetting disables emergency pumps.",
            "Incorporate dynamic rate-of-change thresholds and evidential belief bounds requiring high confidence before triggering isolation."
        ],
        [
            "4. Component Procurement Lead Time Delays",
            "Shipping delays for specialized industrial sensors delay hardware development.",
            "Finalize specifications in Month 6; initiate procurement through institutional channels early; utilize common multi-source equivalents."
        ],
        [
            "5. Laboratory Electrical Hazard Risk",
            "Risk of electrical shock to personnel during fluid and electrical testing.",
            "Strict experimental boundary: strictly low-voltage DC/AC (<= 24 V, <= 2 A); complete galvanic isolation; acrylic shielding and physical interlocks."
        ],
        [
            "6. Research Novelty Overlap with Commercial Devices",
            "Risk of duplicating proprietary industrial switchgear logic.",
            "Maintain focus on academic scientific contributions: online sensor fault diagnosis, evidential uncertainty fusion, and open benchmarking."
        ]
    ]
    t4_widths = [Inches(1.8), Inches(2.2), Inches(2.5)]
    table4 = doc.add_table(rows=len(t4_data) + 1, cols=3)
    format_table(table4, t4_widths, t4_headers, t4_data)

    # =========================================================================
    # SECTION 11
    # =========================================================================
    add_h1("11. Environmental Impact and Safety")

    add_p(
        "The project is structured with an unwavering commitment to environmental sustainability and rigorous laboratory safety:"
    )

    add_bullet(
        "Environmental Sustainability and E-Waste Management: ",
        "The investigation is fundamentally computational and laboratory-scale. Energy consumption is negligible, restricted to standard low-power "
        "microcontroller hardware and bench workstations. All circuit prototyping strictly utilizes RoHS-compliant (Restriction of Hazardous Substances) "
        "components and lead-free solder. End-of-life electronic prototyping materials, depleted boards, and wiring will be cataloged and disposed of "
        "strictly through institutional electronic waste disposal channels in compliance with national e-waste management rules."
    )
    add_bullet(
        "Fluid Management and Conservation: ",
        "Experimental water testing will be conducted within a sealed, closed-loop acrylic test chamber. Non-potable test water is contained in a "
        "recirculating reservoir, eliminating water wastage and ensuring that no fluid discharges into municipal stormwater drains."
    )
    add_bullet(
        "Strict Laboratory Electrical Safety Protocol: ",
        "A mandatory safety protocol governs all physical experimentation: (a) Absolute prohibition of live AC mains electricity (230 V) in the presence "
        "of water; (b) All physical testing is restricted strictly to an isolated, current-limited, low-voltage bench power supply (maximum 24 V DC / 24 V AC, "
        "current limited to < 2 A); (c) The physical experimental chamber features transparent shatterproof polycarbonate shielding, "
        "dual emergency-stop disconnect buttons, and electrical interlocks that de-energize the bench circuit immediately upon opening the access lid; "
        "(d) All testing is conducted under direct faculty supervision within the department electronics laboratory."
    )

    # =========================================================================
    # SECTION 12
    # =========================================================================
    add_h1("12. Expected Impact and Utilisation")

    add_p(
        "The outcomes of this research address critical societal, infrastructural, and academic priorities in climate disaster resilience:"
    )

    add_bullet(
        "Relevance to Climate-Resilient Infrastructure: ",
        "Flood-prone residential dwellings, rural healthcare dispensaries, public schools, and community shelters are highly vulnerable to catastrophic "
        "electrical failures during monsoon inundations. Developing an intelligent, localized hazard prediction and isolation framework provides "
        "a scientific blueprint for building-level electrical protection that prevents electrocution while preserving emergency utility power."
    )
    add_bullet(
        "Academic and Methodological Impact: ",
        "The project bridges a long-standing division between civil/environmental flood telemetry and electrical switchgear engineering. By establishing "
        "how sensor-health analytics and evidential reasoning improve safety-critical embedded decisions, the project contributes foundational knowledge "
        "disseminated through international peer-reviewed journals."
    )
    add_bullet(
        "Clear Boundary and Translational Pathway: ",
        "It is emphasized that the deliverable of this 36-month project is a laboratory-validated proof-of-concept framework and demonstrator, "
        "not a commercially certified consumer electrical safety breaker. Full translational deployment in commercial residential installations "
        "would require subsequent developmental phases: (a) industrial enclosure engineering rated to IP67/NEMA 4X; (b) formal functional safety "
        "certification under IEC 61508 / ISO 13849; (c) third-party high-voltage type-testing under IEC 60947 / UL 489; and (d) controlled pilot field trials "
        "in collaboration with certified switchgear manufacturers and municipal electrical utility boards."
    )

    # =========================================================================
    # SECTION 13
    # =========================================================================
    add_h1("13. Principal Investigator and Available Facilities")

    add_p(
        "Principal Investigator Profile: Dr. Dhanalakshmi Banavath is an Assistant Professor in the Department of Electronics and Communication "
        "Engineering. Her research specialization centers on embedded systems, sensor technologies, signal processing, and secure hardware "
        "architectures. Her academic background provides the necessary expertise in microcontrollers, sensor interfacing, digital signal processing, "
        "and embedded firmware development required to lead and execute this interdisciplinary project. In accordance with the ANRF-IRG scheme "
        "guidelines for individual-centric grants, the project will be executed without a Co-Investigator, with collaboration restricted to the "
        "parent Department of Electronics and Communication Engineering."
    )

    add_p(
        "Available Institutional Facilities: The host institution provides robust physical and computational infrastructure to fully support the "
        "proposed 36-month investigation. The PI has access to modern computing workstations equipped with industry-standard engineering simulation "
        "environments (including numerical computing software and circuit simulation packages) for executing the Phase 1 computational modelling. "
        "Furthermore, the Department of Electronics and Communication Engineering hosts well-equipped electronics laboratories featuring regulated "
        "benchtop power supplies, digital storage oscilloscopes (DSOs), arbitrary function generators, precision digital multimeters, logic analyzers, "
        "embedded development toolchains, and PCB prototyping/soldering workstations. These confirmed facilities ensure that both simulation and "
        "safe low-voltage laboratory validation can be executed rigorously without institutional impediments."
    )

    # =========================================================================
    # SECTION 14
    # =========================================================================
    add_h1("14. Project Management and Implementation")

    add_p(
        "The Principal Investigator will maintain comprehensive administrative, technical, and safety stewardship over the entire project lifecycle:"
    )

    add_bullet(
        "Technical Leadership: ",
        "Directly formulating mathematical hazard models, designing sensor fault diagnosis algorithms, authoring embedded firmware in C/C++, "
        "and supervising circuit schematic capture and PCB layouts."
    )
    add_bullet(
        "Laboratory Safety Governance: ",
        "Enforcing strict compliance with low-voltage safety boundaries (≤ 24 V), conducting mandatory pre-experiment safety audits, "
        "and supervising all fluid and electrical bench testing."
    )
    add_bullet(
        "Procurement and Financial Oversight: ",
        "Coordinating the timely specification and procurement of project components and consumables through established institutional procurement "
        "committees, maintaining project financial ledgers in strict accordance with ANRF financial norms."
    )
    add_bullet(
        "Research Dissemination and Reporting: ",
        "Compiling empirical datasets, authoring peer-reviewed manuscripts for high-impact journals, and submitting annual technical and financial "
        "progress reports and the final project completion dossier to ANRF."
    )

    # =========================================================================
    # SECTION 15
    # =========================================================================
    add_h1("15. References")

    references_list = [
        "Basha, E., Ravela, S., & Rus, D. (2008). Model-based monitoring for early warning flood detection. In Proceedings of the 6th ACM Conference on Embedded Networked Sensor Systems (SenSys '08), Raleigh, NC, USA, pp. 295–308. https://doi.org/10.1145/1460412.1460442",
        "Bureau of Indian Standards (BIS). (2016). National Building Code of India 2016 (SP 7: 2016), Part 8: Building Services, Section 2: Electrical and Allied Installations. New Delhi: Bureau of Indian Standards.",
        "Castanedo, F. (2013). A review of data fusion techniques. The Scientific World Journal, Vol. 2013, Article ID 704504, pp. 1–19. https://doi.org/10.1155/2013/704504",
        "Central Electricity Authority (CEA). (2010). Central Electricity Authority (Measures relating to Safety and Electric Supply) Regulations, 2010. New Delhi: Ministry of Power, Government of India.",
        "Dempster, A. P. (1967). Upper and lower probabilities induced by a multivalued mapping. The Annals of Mathematical Statistics, 38(2), pp. 325–339. https://doi.org/10.1214/aoms/1177698950",
        "Depari, S. S. S. R., Wibowo, P., & Siregar, R. (2020). Prototype of automated electrical power disconnection based on water level sensor. In 2020 International Conference on Applied Science and Technology (iCAST), Padang, Indonesia, pp. 412–416. https://doi.org/10.1109/iCAST51016.2020.9557620",
        "Federal Emergency Management Agency (FEMA). (2017). Protecting Building Utility Systems From Flood Damage: Principles and Practices for the Design and Construction of Flood Resistant Building Utility Systems (FEMA P-348, Edition 2). Washington, D.C.: FEMA.",
        "Hall, D. L., & Llinas, J. (1997). An introduction to multisensor data fusion. Proceedings of the IEEE, 85(1), pp. 6–23. https://doi.org/10.1109/5.554205",
        "International Electrotechnical Commission (IEC). (2010). Functional safety of electrical/electronic/programmable electronic safety-related systems - Part 1: General requirements (IEC Standard No. 61508-1:2010). Geneva: IEC.",
        "International Electrotechnical Commission (IEC). (2017). Low-voltage electrical installations - Part 4-41: Protection for safety - Protection against electric shock (IEC Standard No. 60364-4-41:2005+AMD1:2017). Geneva: IEC.",
        "International Organization for Standardization (ISO). (2015). Safety of machinery - Safety-related parts of control systems - Part 1: General principles for design (ISO Standard No. 13849-1:2015). Geneva: ISO.",
        "Lo, C. H., & Ansari, N. (2012). The progressive smart grid: A survey on decentralized controls and communications. IEEE Communications Surveys & Tutorials, 14(3), pp. 701–721. https://doi.org/10.1109/SURV.2011.072810.00019",
        "Mahapatro, A., & Khilar, P. M. (2013). Fault diagnosis in wireless sensor networks: A survey. IEEE Communications Surveys & Tutorials, 15(4), pp. 2000–2026. https://doi.org/10.1109/SURV.2013.030713.00062",
        "Mydlarz, C., Challagonda, P., Steers, B., Rucker, J., Brain, T., Branco, B., Burnett, H. E., Kaur, A., Fischman, R., Graziano, K., Krueger, K., Hénaff, E., Ignace, V., Jozwiak, E., Palchuri, J., Pierone, P., Rothman, P., Toledo-Crow, R., & Silverman, A. I. (2024). FloodNet: Low-cost ultrasonic sensors for real-time measurement of hyperlocal, street-level floods in New York City. Water Resources Research, 60(5), Article e2023WR036806. https://doi.org/10.1029/2023WR036806",
        "National Disaster Management Authority (NDMA). (2010). National Disaster Management Guidelines: Management of Urban Flooding. New Delhi: Government of India.",
        "National Fire Protection Association (NFPA). (2023). NFPA 70: National Electrical Code (NEC) (2023 Edition). Quincy, MA: NFPA.",
        "Ni, K., Ramanathan, N., Chehade, M. N. H., Balzano, L., Nair, S., Zahedi, S., Kohler, E., Govindan, R., & Srivastava, M. (2009). Sensor network data fault types. ACM Transactions on Sensor Networks, 5(3), Article 25, pp. 1–29. https://doi.org/10.1145/1525856.1525863",
        "Shafer, G. (1976). A Mathematical Theory of Evidence. Princeton, NJ: Princeton University Press.",
        "Sharma, A. B., Golubchik, L., & Govindan, R. (2010). Sensor faults: Detection methods and prevalence in real-world datasets. ACM Transactions on Sensor Networks, 6(3), Article 23, pp. 1–39. https://doi.org/10.1145/1754414.1754419",
        "Zhang, Y.,纤维, N., & Havinga, P. (2010). Outlier detection techniques for wireless sensor networks: A survey. IEEE Communications Surveys & Tutorials, 12(2), pp. 159–170. https://doi.org/10.1109/SURV.2010.021510.00047"
    ]

    # Correct any character in Zhang reference:
    references_list[-1] = "Zhang, Y., Meratnia, N., & Havinga, P. (2010). Outlier detection techniques for wireless sensor networks: A survey. IEEE Communications Surveys & Tutorials, 12(2), pp. 159–170. https://doi.org/10.1109/SURV.2010.021510.00047"

    for ref in references_list:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.12
        p_ref.paragraph_format.left_indent = Inches(0.5)
        p_ref.paragraph_format.first_line_indent = Inches(-0.5)
        run_r = p_ref.add_run(ref)
        run_r.font.name = 'Times New Roman'
        run_r.font.size = Pt(9.5)

    # Add Page Numbers to Footers
    add_footer_page_numbers(doc)

    # Save DOCX
    doc.save(output_docx_path)
    print(f"Document saved successfully as '{output_docx_path}'")

if __name__ == '__main__':
    out_docx = os.path.abspath('ANRF_IRG_Technical_Proposal.docx')
    build_proposal_doc(out_docx)
