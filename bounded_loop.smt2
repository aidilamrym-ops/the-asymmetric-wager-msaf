; bounded_loop -- the Gödelian Compliance Loop (Protocol 09) -- finite-state
; specification and machine check.  Renamed and re-tokenised by Fase A12
; (2026-10-07) per KAMUS_PEMETAAN.md; the mathematical object is unchanged.
; Original A1 names: protocol_09.smt2 with tokens P09/SCAN/SELFCHECK/HALT/M/N.
; and machine check.  Closes F0_REPORT.md section 9 residual 1 (A1) and the
; "cannot be written off-hand" paragraph of SOLVABLE_FINITE_PARADOX.md section
; 1.B, both of which named the same three missing pieces: transition relation,
; self-reference operator, step counter.  All three are below.
;
; WHAT THE LOOP IS
;   A standalone recursive function that continuously verifies every protocol
;   in S_Protocol -- including the specification of the loop itself -- and
;   stops only when the whole set has been verified (Protocol 09, section 1
;   of SOLVABLE_FINITE_PARADOX.md).
;
; THE FINITE STATE MACHINE
;   Control states (finite, three of them):
;     q_scan       examining protocol i
;     q_check  the scan has reached the loop's own specification
;     q_halt       every protocol verified; the loop has stopped
;   Configuration: (q, i, b) -- control state, protocol index, step counter.
;
;   d  q_scan, i < p09_op   ->  q_scan,  i := i + 1     ordinary step
;   d  q_scan, i = p09_op   ->  q_check, i := 0     SELF-REFERENCE: the loop
;                                                meets its own specification
;                                                and re-runs the whole pass
;   d  q_scan, i > p09_op   ->  q_halt                  completion
;   d  q_check       ->  q_scan,  i := 0         the pass restarts
;   d  q_halt            ->  q_halt                  absorbing
;
;   Step counter: b' = b + 1 on every transition, b >= 0.  The budget is n_budget.
;
;   The third rule is unreachable while A3 holds: a scan starting at i = 0
;   meets i = p09_op before it could exceed it, and the q_check rule sends it
;   back to 0.  It is written down anyway because it is what "completion"
;   would have to mean, and because A5 constrains q_halt however it was entered.
;
; WHAT IS PROVED, AND WHAT IS NOT
;   The claim, which is the last assertion by the auditor's convention, is:
;   a configuration in which the loop has halted inside the step budget.
;   The context alone is satisfiable, so the script is not vacuous; the
;   contradiction needs three axioms plus the claim.
;
;   Those three, by 0-based position in the list of (assert ...) forms, are
;   [11] A4 the invariant b >= i, [12] A5 q_halt implies i >= m_budget, [13] A6
;   m_budget > n_budget, and the claim itself.  Drop any one of them and Z3 reports sat.
;   The other thirteen assertions are specification: they fix the machine
;   being talked about, and the auditor reports that the proof does not rest
;   on them.  That is the honest shape -- a machine described in full, and a
;   bound derived from the three lines that actually carry it.
;
;   The self-reference rule d(q_scan, i = p09_op) is a *second, independent*
;   obstruction -- it sends the scan back to i = 0, so the pass it restarted
;   never reaches q_halt at all.  That unreachability is a reachability
;   property and is NOT what this script discharges; a quantifier-free
;   single-step encoding cannot state it.  This script discharges the bound:
;   completion requires examining all m_budget protocols, the invariant says the
;   step counter is never behind the index, and m_budget exceeds the budget n_budget.
;   Two obstructions, only one of them machine-checked here.  Stating which
;   is which is the difference between this file and the off-hand encoding
;   that section 1.B correctly refused to accept.
;
; WHAT NO VERDICT HERE SETTLES
;   A GENUINE verdict says this encoding is non-circular.  It says nothing
;   about whether the encoding matches the mathematics, and it settles no
;   open problem.
(set-logic QF_LIA)

; The three control states are named Int constants rather than a datatype so
; that the script stays inside QF_LIA, which is decidable and cannot return
; "unknown".  Finiteness is explicit: the assertions below restrict q0 and q1
; to exactly these three values.
(define-fun q_scan () Int 0)
(define-fun q_check () Int 1)
(define-fun q_halt () Int 2)

; configuration at the current step and at the next step
(declare-const q0 Int)
(declare-const q1 Int)
(declare-const i0 Int)
(declare-const i1 Int)
(declare-const b0 Int)
(declare-const b1 Int)

; p09_op -- the self-reference operator: the index at which the scan encounters
; the specification of the loop itself.  m_budget -- how many protocols must be
; examined before the loop may halt.  n_budget -- the step budget.
(declare-const p09_op Int)
(declare-const m_budget Int)
(declare-const n_budget Int)

; ---------------------------------------------------------------- context --
; A0 -- the control state is one of the three, at both ends of the step
(assert (or (= q0 q_scan) (= q0 q_check) (= q0 q_halt)))
(assert (or (= q1 q_scan) (= q1 q_check) (= q1 q_halt)))

; A1 -- the step counter advances by exactly one and never goes negative
(assert (= b1 (+ b0 1)))
(assert (>= b0 0))

; A2 -- the transition relation, one symbolic step
(assert (=> (and (= q0 q_scan) (< i0 p09_op))
            (and (= q1 q_scan) (= i1 (+ i0 1)))))
(assert (=> (and (= q0 q_scan) (= i0 p09_op))
            (and (= q1 q_check) (= i1 0))))
(assert (=> (and (= q0 q_scan) (> i0 p09_op))
            (= q1 q_halt)))
(assert (=> (= q0 q_check)
            (and (= q1 q_scan) (= i1 0))))
(assert (=> (= q0 q_halt)
            (and (= q1 q_halt) (= i1 i0))))

; A3 -- the self-reference operator sits strictly inside the scanned range,
;       so the q_check rule above is reachable and is not decoration
(assert (>= p09_op 0))
(assert (< p09_op m_budget))

; A4 -- invariant: the step counter is never behind the protocol index.
;       i starts at 0; i grows only on a transition that also grows b by one;
;       the only place i falls is the q_check reset, where i goes to 0.
(assert (>= b0 i0))

; A5 -- completion: q_halt is entered only from a scan whose index has already
;       reached m_budget, and A2's q_halt rule preserves i, so i >= m_budget holds at q_halt
(assert (=> (= q0 q_halt) (>= i0 m_budget)))

; A6 -- the protocol set is not covered by the step budget, and the budget
;       is a positive finite number rather than infinity
(assert (> m_budget n_budget))
(assert (> n_budget 0))

; ------------------------------------------------------------------ claim --
; A loop that has halted inside its budget.  Last assertion on purpose: the
; circularity auditor takes the final (assert ...) as the claim and treats
; everything above it as context.
(assert (and (= q0 q_halt) (<= b0 n_budget)))

; MACHINE RESULT: unsat
; Recorded in the sidecar run log bounded_loop.log.  A displayed verdict with
; no run log is a claim and not a result -- the defect F0-3 found in section
; 1.B of SOLVABLE_FINITE_PARADOX.md -- so this line exists to make the
; Anti-Circularity claim gate refuse the file if the log ever goes missing.
(check-sat)
(exit)
