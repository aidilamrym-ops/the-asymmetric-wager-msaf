; Protocol 09 -- the Gödelian Compliance Loop -- finite-state specification
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
;     SCAN       examining protocol i
;     SELFCHECK  the scan has reached the loop's own specification
;     HALT       every protocol verified; the loop has stopped
;   Configuration: (q, i, b) -- control state, protocol index, step counter.
;
;   d  SCAN, i < P09   ->  SCAN,  i := i + 1     ordinary step
;   d  SCAN, i = P09   ->  SELFCHECK, i := 0     SELF-REFERENCE: the loop
;                                                meets its own specification
;                                                and re-runs the whole pass
;   d  SCAN, i > P09   ->  HALT                  completion
;   d  SELFCHECK       ->  SCAN,  i := 0         the pass restarts
;   d  HALT            ->  HALT                  absorbing
;
;   Step counter: b' = b + 1 on every transition, b >= 0.  The budget is N.
;
;   The third rule is unreachable while A3 holds: a scan starting at i = 0
;   meets i = P09 before it could exceed it, and the SELFCHECK rule sends it
;   back to 0.  It is written down anyway because it is what "completion"
;   would have to mean, and because A5 constrains HALT however it was entered.
;
; WHAT IS PROVED, AND WHAT IS NOT
;   The claim, which is the last assertion by the auditor's convention, is:
;   a configuration in which the loop has halted inside the step budget.
;   The context alone is satisfiable, so the script is not vacuous; the
;   contradiction needs three axioms plus the claim.
;
;   Those three, by 0-based position in the list of (assert ...) forms, are
;   [11] A4 the invariant b >= i, [12] A5 HALT implies i >= M, [13] A6
;   M > N, and the claim itself.  Drop any one of them and Z3 reports sat.
;   The other thirteen assertions are specification: they fix the machine
;   being talked about, and the auditor reports that the proof does not rest
;   on them.  That is the honest shape -- a machine described in full, and a
;   bound derived from the three lines that actually carry it.
;
;   The self-reference rule d(SCAN, i = P09) is a *second, independent*
;   obstruction -- it sends the scan back to i = 0, so the pass it restarted
;   never reaches HALT at all.  That unreachability is a reachability
;   property and is NOT what this script discharges; a quantifier-free
;   single-step encoding cannot state it.  This script discharges the bound:
;   completion requires examining all M protocols, the invariant says the
;   step counter is never behind the index, and M exceeds the budget N.
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
(define-fun SCAN () Int 0)
(define-fun SELFCHECK () Int 1)
(define-fun HALT () Int 2)

; configuration at the current step and at the next step
(declare-const q0 Int)
(declare-const q1 Int)
(declare-const i0 Int)
(declare-const i1 Int)
(declare-const b0 Int)
(declare-const b1 Int)

; P09 -- the self-reference operator: the index at which the scan encounters
; the specification of the loop itself.  M -- how many protocols must be
; examined before the loop may halt.  N -- the step budget.
(declare-const P09 Int)
(declare-const M Int)
(declare-const N Int)

; ---------------------------------------------------------------- context --
; A0 -- the control state is one of the three, at both ends of the step
(assert (or (= q0 SCAN) (= q0 SELFCHECK) (= q0 HALT)))
(assert (or (= q1 SCAN) (= q1 SELFCHECK) (= q1 HALT)))

; A1 -- the step counter advances by exactly one and never goes negative
(assert (= b1 (+ b0 1)))
(assert (>= b0 0))

; A2 -- the transition relation, one symbolic step
(assert (=> (and (= q0 SCAN) (< i0 P09))
            (and (= q1 SCAN) (= i1 (+ i0 1)))))
(assert (=> (and (= q0 SCAN) (= i0 P09))
            (and (= q1 SELFCHECK) (= i1 0))))
(assert (=> (and (= q0 SCAN) (> i0 P09))
            (= q1 HALT)))
(assert (=> (= q0 SELFCHECK)
            (and (= q1 SCAN) (= i1 0))))
(assert (=> (= q0 HALT)
            (and (= q1 HALT) (= i1 i0))))

; A3 -- the self-reference operator sits strictly inside the scanned range,
;       so the SELFCHECK rule above is reachable and is not decoration
(assert (>= P09 0))
(assert (< P09 M))

; A4 -- invariant: the step counter is never behind the protocol index.
;       i starts at 0; i grows only on a transition that also grows b by one;
;       the only place i falls is the SELFCHECK reset, where i goes to 0.
(assert (>= b0 i0))

; A5 -- completion: HALT is entered only from a scan whose index has already
;       reached M, and A2's HALT rule preserves i, so i >= M holds at HALT
(assert (=> (= q0 HALT) (>= i0 M)))

; A6 -- the protocol set is not covered by the step budget, and the budget
;       is a positive finite number rather than infinity
(assert (> M N))
(assert (> N 0))

; ------------------------------------------------------------------ claim --
; A loop that has halted inside its budget.  Last assertion on purpose: the
; circularity auditor takes the final (assert ...) as the claim and treats
; everything above it as context.
(assert (and (= q0 HALT) (<= b0 N)))

; MACHINE RESULT: unsat
; Recorded in the sidecar run log protocol_09.log.  A displayed verdict with
; no run log is a claim and not a result -- the defect F0-3 found in section
; 1.B of SOLVABLE_FINITE_PARADOX.md -- so this line exists to make the
; Anti-Circularity claim gate refuse the file if the log ever goes missing.
(check-sat)
(exit)
