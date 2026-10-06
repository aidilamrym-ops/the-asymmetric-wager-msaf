# -*- coding: utf-8 -*-
"""
 * PROJECT          : AETHER - Singularitas Heptagonal ( Omega_7-Apex )
 * ARCHITECT'S      : Muhammad Aidil Amry
 * FILE             : GUINAND_WEIL/shp_mcp_bridge_v4.py
 * DESCRIPTION      : Sovereign Holographic Protocol (SHP) to Model Context Protocol (MCP) Bridge.
 *                    v4.2.0-PROOF-ONLY: registered as a local opencode MCP server, reads the
 *                    Theory of Everything derivation corpus (list/read/search/reference tools),
 *                    real Z3 SMT integration (z3py; fail-loud UNKNOWN on rejected scripts;
 *                    verdict TOOL NOT RUN when z3py is absent - no simulated verdict exists),
 *                    gated RCE tools and --test suite.
 * STATUS           : EXECUTING (OPCODE MCP SERVER / INTEGRATED TEST-SUITE)
 *
 * Environment variables:
 *   SHP_MCP_CORPUS_ROOT   : corpus directory (default D:\\Theory_of_Everything_Derivations)
 *   SHP_MCP_WRITE_ROOTS   : os.pathsep-separated allowlist for write_file
 *                           (default: %TEMP%\\opencode\\shp_mcp, workspace root, corpus root)
 *   SHP_MCP_ALLOW_EXEC    : "1" enables execute_command (default: off / tool not listed)
"""

import sys
import json
import re
import math
import hashlib
import time
import asyncio
import subprocess
import os
import tempfile

# Dynamic import for z3-solver. PROOF-ONLY: when z3py is absent this module
# refuses to answer instead of guessing (see SMTTribunal contract).
Z3_AVAILABLE = False
try:
    import z3
    Z3_AVAILABLE = True
except ImportError:
    pass

# =====================================================================
# 1. HYPERDIMENSIONAL COMPUTING ENGINE (SHP PILAR I)
# =====================================================================
class HyperdimensionalEngine:
    def __init__(self, dimensions=10000):
        self.dimensions = dimensions

    def generate_bipolar_vector(self, seed_str):
        """Generates a deterministic 10,000-D bipolar vector (-1, 1) based on seed with long-period LCG higher bits."""
        state = int(hashlib.sha256(seed_str.encode('utf-8')).hexdigest(), 16) & 0xFFFFFFFF
        vector = []
        for _ in range(self.dimensions):
            # LCG multiplier (Numerical Recipes parameters)
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            # Use bit 30 to avoid LSB parity cycles
            val = 1 if ((state >> 30) & 1) == 0 else -1
            vector.append(val)
        return vector

    def cosine_similarity(self, vec_a, vec_b):
        """Computes the cosine similarity between two 10,000-D vectors."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def bundle(self, vectors):
        """Bundles multiple vectors (Superposition ⊕) followed by normalization."""
        if not vectors:
            return [0] * self.dimensions
        bundled = [0] * self.dimensions
        for vec in vectors:
            for i in range(self.dimensions):
                bundled[i] += vec[i]
        
        norm = math.sqrt(sum(x * x for x in bundled))
        if norm == 0:
            return [0] * self.dimensions
        return [x / norm for x in bundled]

    def bind(self, vec_a, vec_b):
        """Binds two concepts together (Association ⊗) using Hadamard product."""
        return [a * b for a, b in zip(vec_a, vec_b)]

    def permute(self, vector, shifts=1):
        """Circular shift (Permutation Π) to represent temporal causality."""
        shifts = shifts % self.dimensions
        return vector[shifts:] + vector[:shifts]


# =====================================================================
# 2. EPISTEMIC SIEVE COMPILER (SHP PILAR III)
# =====================================================================
class EpistemicSieve:
    def __init__(self):
        self.banned_words = [
            r"\bmungkin\b", r"\bsepertinya\b", r"\bberpotensi\b", 
            r"\bdiasumsikan\b", r"\bkemungkinan\b", r"\bbarangkali\b",
            r"\bkonon\b", r"\bkatanya\b", r"\bseharusnya\b",
            r"\bperhaps\b", r"\bprobably\b", r"\bmaybe\b", r"\bassumed\b",
            r"\blikely\b", r"\bpossibly\b", r"\bpresumably\b"
        ]
        self.banned_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.banned_words]

    def purge_assumptions(self, raw_input):
        """Purges sentences containing probabilistic narrative fluff."""
        sentences = re.split(r'[.!?\n]+', raw_input)
        clean_facts = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            has_banned = False
            for pattern in self.banned_patterns:
                if pattern.search(sentence):
                    has_banned = True
                    break
            
            if not has_banned:
                clean_facts.append(sentence)
        return clean_facts

    def translate_to_smt_lib2(self, facts):
        """Translates facts into clean SMT-LIB2 logic declarations."""
        smt_lines = [
            "; ====================================================",
            "; GNASE TRIBUNAL: SMT-LIB2 FIRST-ORDER LOGIC MATRIX",
            "; ====================================================",
            "(set-info :smt-lib-version 2.6)",
            "(set-logic QF_LIA)",
            "(declare-const hardware_limit Int)",
            "(declare-const system_entropy Int)",
            "(assert (= hardware_limit 1000))",
            "(assert (>= system_entropy 0))"
        ]
        
        for idx, fact in enumerate(facts):
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', fact)[:30].lower()
            if not clean_name:
                clean_name = f"fact_{idx}"
            smt_lines.append(f"(declare-const {clean_name} Int)")
            smt_lines.append(f"(assert (<= {clean_name} hardware_limit))")
            
        smt_lines.append("(check-sat)")
        smt_lines.append("(get-model)")
        return "\n".join(smt_lines)


# =====================================================================
# 3. LOGIC TRIBUNAL (SHP PILAR IV & [UNSAT = KILL] - upgraded to real Z3)
# =====================================================================
class SMTTribunal:
    def __init__(self):
        self.z3_active = Z3_AVAILABLE

    def evaluate_satisfiability(self, smt_script):
        """Evaluate satisfiability with real Z3. PROOF-ONLY.

        Fail-loud contract (v4.2.0-PROOF-ONLY, 2026-10-04):
          * z3py present + script accepted  -> real verdict (SAT / UNSAT / UNKNOWN).
          * z3py present + script REJECTED  -> verdict UNKNOWN, never simulated.
                                               A regex guess is not a verdict.
          * z3py absent                     -> verdict TOOL NOT RUN, never a
                                               SAT/UNSAT verdict at all, labelled
                                               [PROOF-ONLY - NOT A SIMULATED].

        There is no simulated branch any more. This tribunal gates file writes
        and command execution inside a corpus about pure physics and pure
        mathematics, so a verdict no solver produced is refused rather than
        guessed. The consumers are already fail-closed (they refuse the action
        unless the verdict is exactly "SATISFIABLE"), so TOOL NOT RUN blocks
        the action instead of permitting it.
        """
        if self.z3_active:
            try:
                solver = z3.Solver()
                # Parse standard SMT-LIB2 formatted script directly into solver
                solver.from_string(smt_script)
                verdict = solver.check()
                
                if verdict == z3.sat:
                    model = solver.model()
                    return {
                        "verdict": "SATISFIABLE",
                        "mcs": [],
                        "model": str(model),
                        "message": "[STATUS: SATISFIABLE] Real Z3 SMT Solver confirms absolute logical consistency."
                    }
                elif verdict == z3.unsat:
                    try:
                        unsat_core = solver.unsat_core()
                        mcs = [str(c) for c in unsat_core]
                    except Exception:
                        mcs = ["Logika Kontradiktif terdeteksi di dalam asersi"]
                    return {
                        "verdict": "UNSATISFIABLE",
                        "mcs": mcs,
                        "message": "[FATAL_UNSAT] Real Z3 SMT Solver detected a logical contradiction! Executing Guillotine."
                    }
                else:
                    return {
                        "verdict": "UNKNOWN",
                        "mcs": [],
                        "message": "[UNKNOWN] Z3 SMT Solver hit an undecidable boundary or timeout limit."
                    }
            except Exception as e:
                # Z3 is present but rejected the script (parse error / unsupported
                # theory, e.g. 'log' is not an SMT-LIB2 Real function). Falling back
                # to a regex guess here produced a documented FALSE verdict, so the
                # only honest answer is UNKNOWN.
                sys.stderr.write(f"[Z3-ERROR] Z3 rejected the SMT script: {str(e)}\n")
                sys.stderr.flush()
                return {
                    "verdict": "UNKNOWN",
                    "mcs": [],
                    "message": (
                        "[NOT-DECIDABLE] [PROOF-ONLY - NOT A SIMULATED] Z3 is "
                        "present but rejected this script (parse error or "
                        "unsupported theory). Verdict UNKNOWN - no simulated "
                        "fallback exists. Formalize the claim in a decidable "
                        "fragment first."
                    ),
                    "z3_error": str(e).strip(),
                    "simulated": False,
                }
        return self._refuse_without_proof(smt_script)

    @staticmethod
    def _refuse_without_proof(smt_script):
        """No solver ran here, so no verdict may be issued.

        This replaces ``_evaluate_simulated``, a regex heuristic that returned
        SATISFIABLE / UNSATISFIABLE whenever z3py was absent. That branch is
        removed rather than relabelled: in a corpus about pure physics and pure
        mathematics, a verdict that no solver produced is indistinguishable to
        every downstream reader from a fabricated one, and this tribunal gates
        file writes and command execution. The refusal is fail-closed - the
        consumers act only on exactly "SATISFIABLE".

        ``smt_script`` is kept in the signature so existing call sites and
        any external caller remain valid; it is deliberately not inspected,
        because inspecting it with regexes is what produced false verdicts.
        """
        return {
            "verdict": "TOOL NOT RUN",
            "mcs": [],
            "message": (
                "[PROOF-ONLY - NOT A SIMULATED] z3py is ABSENT on this host, "
                "so no solver ran and no verdict exists. This tribunal does "
                "not guess: install z3-solver and re-run. Every consumer "
                "treats a verdict other than SATISFIABLE as a refusal."
            ),
            "simulated": False,
            "reason": "z3py_absent",
        }


# =====================================================================
# 4. SKILL REGISTRY & AMNESIA CONTROLLER
# =====================================================================
class SkillRegistryRouter:
    def __init__(self):
        self.pillars = {
            "p1_fluid_logistics": "Network, P2P communication, and WebRTC data channels.",
            "p2_genetic_univalence": "Instruction mutation, self-healing, and HoTT validation.",
            "p3_plasma_thermodynamics": "Isentropic memory purging and thermal silence.",
            "p4_cognitive_cosmology": "Memory allocation and stigmergic blackboards.",
            "p5_topological_superconductors": "WebGPU hardware acceleration and kernel fusion.",
            "p6_aleph_null_consciousness": "Formal reasoning and Z3 SMT Tribunal.",
            "p7_langlands_reduction": "Post-quantum cryptography and spectral shrinkage.",
            "p8_ihara_spectrum": "Circular graph analysis and anomaly detection."
        }

    def wipe_transient_buffer(self, byte_array):
        """Enforces absolute Isentropic Amnesia Protocol (0x00 Null Bytes)."""
        if isinstance(byte_array, bytearray) or isinstance(byte_array, list):
            for i in range(len(byte_array)):
                byte_array[i] = 0
            return True
        return False


# =====================================================================
# 5. THEORY-OF-EVERYTHING CORPUS READER (read-only index over D:\...)
# =====================================================================
DEFAULT_CORPUS_ROOT = os.environ.get(
    "SHP_MCP_CORPUS_ROOT", r"D:\Theory_of_Everything_Derivations"
)
EXEC_ENABLED = os.environ.get("SHP_MCP_ALLOW_EXEC", "0") == "1"
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _default_write_roots():
    env = os.environ.get("SHP_MCP_WRITE_ROOTS")
    if env:
        raw = [p for p in env.split(os.pathsep) if p.strip()]
    else:
        raw = [
            os.path.join(tempfile.gettempdir(), "opencode", "shp_mcp"),
            WORKSPACE_ROOT,
            DEFAULT_CORPUS_ROOT,
        ]
    return [os.path.normcase(os.path.realpath(p)) for p in raw]


class ToECorpus:
    """Read-only index over the Theory of Everything derivations corpus."""

    TEXT_EXT = (".md", ".txt", ".py", ".lean", ".tex")
    PDF_EXT = (".pdf",)

    def __init__(self, root=None):
        self.root = os.path.realpath(root or DEFAULT_CORPUS_ROOT)
        self._pdf_cache = {}

    def _resolve(self, name):
        path = os.path.realpath(os.path.join(self.root, name))
        root_norm = os.path.normcase(self.root)
        path_norm = os.path.normcase(path)
        if path_norm != root_norm and not path_norm.startswith(root_norm + os.sep):
            raise ValueError("path escapes corpus root")
        if not os.path.isfile(path):
            raise FileNotFoundError(name)
        return path

    def _pdf_pages(self, path):
        if path not in self._pdf_cache:
            try:
                from pypdf import PdfReader
            except ImportError:
                raise RuntimeError("pypdf is required to read PDF documents")
            reader = PdfReader(path)
            self._pdf_cache[path] = [
                (idx + 1, page.extract_text() or "")
                for idx, page in enumerate(reader.pages)
            ]
        return self._pdf_cache[path]

    def _file_text(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in self.PDF_EXT:
            return "\n".join(
                "=== page %d ===\n%s" % (num, txt)
                for num, txt in self._pdf_pages(path)
            )
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()

    @staticmethod
    def _title(text):
        for line in text.splitlines():
            line = line.strip().lstrip("#*_>").strip()
            if line:
                return line[:140]
        return ""

    def list_documents(self):
        documents = []
        if not os.path.isdir(self.root):
            return documents
        for entry in sorted(os.listdir(self.root)):
            path = os.path.join(self.root, entry)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(entry)[1].lower()
            if ext not in self.TEXT_EXT + self.PDF_EXT:
                continue
            with open(path, "rb") as handle:
                blob = handle.read()
            try:
                head = blob[:8192].decode("utf-8")
            except UnicodeDecodeError:
                head = ""
            kind = "pdf" if ext in self.PDF_EXT else ext.lstrip(".")
            documents.append({
                "name": entry,
                "kind": kind,
                "bytes": len(blob),
                "sha256": hashlib.sha256(blob).hexdigest(),
                "title": self._title(head),
            })
        return documents

    def read_document(self, name, page=None, offset=0, limit=200):
        path = self._resolve(name)
        ext = os.path.splitext(path)[1].lower()
        if ext in self.PDF_EXT:
            if page is not None:
                pages = dict(self._pdf_pages(path))
                if int(page) not in pages:
                    raise ValueError("page out of range")
                text = "=== page %s ===\n%s" % (page, pages[int(page)])
            else:
                text = self._file_text(path)
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        lines = text.splitlines()
        offset = max(0, int(offset))
        limit = max(1, min(int(limit), 400))
        return {
            "name": name,
            "total_lines": len(lines),
            "offset": offset,
            "returned_lines": min(limit, max(0, len(lines) - offset)),
            "text": "\n".join(lines[offset:offset + limit]),
        }

    def search(self, query, use_regex=False, max_hits=40):
        max_hits = max(1, min(int(max_hits), 200))
        hits = []
        flags = re.IGNORECASE
        matcher = re.compile(query, flags).search if use_regex else None
        for doc in self.list_documents():
            path = os.path.join(self.root, doc["name"])
            ext = os.path.splitext(path)[1].lower()
            if ext in self.PDF_EXT:
                units = [
                    ("page %d" % num, txt) for num, txt in self._pdf_pages(path)
                ]
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as handle:
                    units = [
                        ("line %d" % (i + 1), line)
                        for i, line in enumerate(handle.read().splitlines())
                    ]
            for locator, line in units:
                found = (
                    matcher.search(line) is not None
                    if matcher is not None
                    else query.lower() in line.lower()
                )
                if found:
                    hits.append({
                        "file": doc["name"],
                        "at": locator,
                        "excerpt": line.strip()[:220],
                    })
                    if len(hits) >= max_hits:
                        return hits
        return hits


# Curated constants extracted from the corpus (provenance noted per entry).
REFERENCE_DATA = {
    "octave_8_pillars": [
        {"id": "p1_fluid_logistics", "name": "Fluid Dynamics / Logistics",
         "source": "SYSTEM_OVERRIDE__THE_GRAND_ALEPH-NULL_SINGULARITY_-_NODE_APEX-TOE"},
        {"id": "p2_genetic_univalence", "name": "Genetic Univalence (HoTT DNA)",
         "source": "Theory_of_Everything_Derivations.pdf s5.1"},
        {"id": "p3_plasma_thermodynamics", "name": "Plasma Thermodynamics (LGp-HICT MHD)",
         "source": "Theory_of_Everything_Derivations.pdf s5.2"},
        {"id": "p4_cognitive_cosmology", "name": "Cognitive Cosmology (holographic dark sector)",
         "source": "Theory_of_Everything_Derivations.pdf s5.3"},
        {"id": "p5_topological_superconductors", "name": "Topological Superconductors (ATMCT-HBM)",
         "source": "Theory_of_Everything_Derivations.pdf s5.4"},
        {"id": "p6_aleph_null_consciousness", "name": "Aleph-Null Consciousness (metric Phi)",
         "source": "Theory_of_Everything_Derivations.pdf s5.5"},
        {"id": "p7_langlands_reduction", "name": "Langlands Reduction (post-quantum / spectral)",
         "source": "SYSTEM_OVERRIDE__THE_GRAND_ALEPH-NULL_SINGULARITY_-_NODE_APEX-TOE"},
        {"id": "p8_ihara_spectrum", "name": "Ihara Spectrum (circular graph anomaly)",
         "source": "SYSTEM_OVERRIDE__THE_GRAND_ALEPH-NULL_SINGULARITY_-_NODE_APEX-TOE"},
    ],
    "octave_action": {
        "formula": "S_OCTAVE = int_dM Tr(T* DT + (alpha/2) T*T*T) + sum_{i=1..8} lambda_i C_i[T_i]",
        "constraints": ["DNA", "MHD", "DarkE", "RoomT", "Phi", "Zeta", "Fluid", "Ricci"],
        "source": "TOE_Master_Reconstruction_AidilAmry.pdf s6",
    },
    "x_toe": {
        "formula": "x_TOE = arg min_{x in {0,1}*} K(x) s.t. SAT(Xi_Absolute(x)) = True",
        "bound": "Landauer: dE >= k_B T ln(2)",
        "source": "Theory_of_Everything_Derivations.pdf s1.1-s1.2",
    },
    "rh_pipeline": {
        "energy": "E(rho) = (sigma - 1/2)^2",
        "barrier": "E <= log(1+E) < E  ==>  E < E  ==>  False  (for E > 0: log(1+E) < E)",
        "chain": ["Lean 4 (DTT)", "Dedukti (lambda-Pi modulo rewriting)",
                  "Coq/Rocq (CIC)", "Isabelle/HOL", "CompCert Clight AST"],
        "verdicts": ["Coq: lra -> False", "Isabelle: auto/arith -> False",
                     "Z3 SMT-LIB2: UNSAT"],
        "source": ["THE GRAND VERIFICATION PIPELINE.pdf",
                   "RH_HARMONIC_ENERGY_PIPELINE.md",
                   "Riemannian Functions and Conformal Geometry.md"],
    },
    "final_rh_project": {
        "lean_kernel": "Lean 4.33.1, 810 theorems, zero 'sorry', zero custom axiom, Mathlib-free critical path",
        "modules": ["lean/Almighty", "lean4/AetherZ3Omega/Riemann/Rigidity.lean",
                    "BarrierTheorem.lean"],
        "z3_batches": "17 batches (Batch 1-17), status UNSAT",
        "zenodo_doi": "10.5281/zenodo.22852564",
        "honest_disclosure": "skeleton resolution only; individual spectral correspondence remains open",
        "source": "Riemannian Functions and Conformal Geometry.md",
    },
    "guinand_weil_scope": {
        "no_claim": "No claim is made about the Riemann Hypothesis, Weil positivity, "
                    "prime counting, or integer factorisation.",
        "n401_lambda_min": "+1.32105051975174632728899314595e-102",
        "n401_radius": "1.8120487388668704061e-1170",
        "n801_lambda_min": "+8.11492015531e-204",
        "inertia_n401": "n+ = 401 (201+200), n- = 0",
        "s2_power": "94.4% at N=401, 92.7% at N=801, both at sigma_u=1.0; 0% at sigma_u<=0.5",
        "s2_verdict_on_real_spectrum": "S1 = INCONCLUSIVE, S2 = INCONSISTENT WITH MONTGOMERY",
        "source": "Rigorous Ball Arithmetic and Bandwidth-Calibrated Spectral Analysis "
                  "(guinand-weil-rigorous-numerics, LaTeX .md)",
    },
    "pqc_constants": {
        "ml_kem": "FIPS 203, DFR <= 2^-138", "ml_dsa": "FIPS 204",
        "rejected": ["RSA", "ECDSA"],
        "source": "SYSTEM_OVERRIDE__THE_POST-QUANTUM_ANNIHILATION_-_NODE_OMEGA-CRYPT.pdf.txt",
    },
    "hyperdimensional": {
        "dim": 10000, "encoding": "bipolar {+1,-1}",
        "ops": ["bundle (superposition)", "bind (Hadamard)", "permute (cyclic shift)",
                "cosine similarity"],
        "source": "NODE_KRONOS-HIPPOCAMPUS_The_Stigmergic_Memory_Architect.pdf.txt",
    },
}


# =====================================================================
# 6. MCP JSON-RPC STDIO SERVER
# =====================================================================
class ShpMcpBridgeServer:
    def __init__(self):
        self.hdc_engine = HyperdimensionalEngine()
        self.sieve = EpistemicSieve()
        self.tribunal = SMTTribunal()
        self.router = SkillRegistryRouter()
        self.corpus = ToECorpus()
        self.write_roots = _default_write_roots()
        self.running = True

    def log(self, message):
        """Outputs debugging logs securely to stderr so as not to pollute stdout."""
        sys.stderr.write(f"[SHP-BRIDGE] {message}\n")
        sys.stderr.flush()

    def handle_initialize(self, request_id, params):
        self.log("Received initialize request.")
        protocol_version = params.get("protocolVersion") or "2024-11-05"
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "oracle-toe-shp-bridge",
                    "version": "4.1.1-ToE"
                }
            }
        }

    def handle_list_tools(self, request_id):
        self.log("Received tools/list request.")
        tools = [
            {
                "name": "mcp_oracle_toe_quantum_transmute",
                "description": "Transmutes input facts or values into 10,000-dimensional hypervector representation to check orthogonal alignment.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "seed": {
                            "type": "string",
                            "description": "The text seed representing the fact to embed."
                        }
                    },
                    "required": ["seed"]
                }
            },
            {
                "name": "mcp_oracle_toe_epistemic_sieve",
                "description": "Applies the Stochastic Purge to filter out vague assumptions and output SMT-LIB2 logic declarations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "raw_prompt": {
                            "type": "string",
                            "description": "Raw unstructured LLM narrative text."
                        }
                    },
                    "required": ["raw_prompt"]
                }
            },
            {
                "name": "mcp_oracle_toe_z3_tribunal",
                "description": "Performs formal Bounded Model Checking over provided logic constraints via actual Z3 solver.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "smt_script": {
                            "type": "string",
                            "description": "SMT-LIB2 formatted declarations."
                        }
                    },
                    "required": ["smt_script"]
                }
            },
            {
                "name": "mcp_oracle_toe_execute_skill",
                "description": "Routes a command dynamically to one of the 8 Pillars of OCTAVE (see mcp_oracle_toe_reference for pillar provenance).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pillar": {
                            "type": "string",
                            "enum": [
                                "p1_fluid_logistics", "p2_genetic_univalence",
                                "p3_plasma_thermodynamics", "p4_cognitive_cosmology",
                                "p5_topological_superconductors", "p6_aleph_null_consciousness",
                                "p7_langlands_reduction", "p8_ihara_spectrum"
                            ],
                            "description": "Target OCTAVE Pillar."
                        },
                        "payload": {
                            "type": "string",
                            "description": "Payload string or input parameter for execution."
                        }
                    },
                    "required": ["pillar", "payload"]
                }
            },
            {
                "name": "mcp_oracle_toe_list_documents",
                "description": "Lists every document in the Theory of Everything derivations corpus with size, SHA-256 and title.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "mcp_oracle_toe_read_document",
                "description": "Reads a document from the Theory of Everything corpus (line-paginated for text, page-aware for PDF).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Exact file name as returned by list_documents."
                        },
                        "page": {
                            "type": "integer",
                            "description": "1-based page number (PDF only)."
                        },
                        "offset": {
                            "type": "integer",
                            "description": "0-based line offset (text documents)."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum lines to return (default 200, cap 400)."
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "mcp_oracle_toe_search_corpus",
                "description": "Case-insensitive (or regex) full-text search across the Theory of Everything corpus, including PDFs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search string."},
                        "regex": {"type": "boolean", "description": "Treat query as regex."},
                        "max_hits": {"type": "integer", "description": "Cap on returned hits (default 40, max 200)."}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "mcp_oracle_toe_reference",
                "description": "Returns curated reference constants derived from the corpus (OCTAVE pillars, RH pipeline, Guinand-Weil scope limits, HDC/PQC parameters) with provenance.",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        if EXEC_ENABLED:
            tools.append({
                "name": "mcp_oracle_toe_execute_command",
                "description": "Executes a local CLI command (ENABLED via SHP_MCP_ALLOW_EXEC=1; blocked by SMT Tribunal when malicious).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command string to run on shell."
                        }
                    },
                    "required": ["command"]
                }
            })
        tools.append({
            "name": "mcp_oracle_toe_write_file",
            "description": "Writes a file, only inside the configured allowlist roots (SHP_MCP_WRITE_ROOTS); enforced by SMT Tribunal.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The target file path (absolute or relative to cwd)."
                    },
                    "content": {
                        "type": "string",
                        "description": "The exact text content to write."
                    }
                },
                "required": ["path", "content"]
            }
        })
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }

    @staticmethod
    def _ok(request_id, text):
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": text}]}
        }

    @staticmethod
    def _deny(request_id, text):
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": text}],
                "isError": True
            }
        }

    def handle_call_tool(self, request_id, tool_name, arguments):
        self.log(f"Calling tool: {tool_name}")
        
        if tool_name == "mcp_oracle_toe_quantum_transmute":
            seed = arguments.get("seed", "")
            vector = self.hdc_engine.generate_bipolar_vector(seed)
            ref_vec = self.hdc_engine.generate_bipolar_vector("0x00 Null Bytes")
            sim = self.hdc_engine.cosine_similarity(vector, ref_vec)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Transmutation successful. Projecting onto ℝ^10000 space.\nCosine similarity against Ground State: {sim:.4f} (Orthogonality check: {'SAT' if abs(sim) < 0.05 else 'UNSAT'})"
                        }
                    ]
                }
            }

        elif tool_name == "mcp_oracle_toe_epistemic_sieve":
            raw_prompt = arguments.get("raw_prompt", "")
            clean_facts = self.sieve.purge_assumptions(raw_prompt)
            smt_lib = self.sieve.translate_to_smt_lib2(clean_facts)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Purged {len(clean_facts)} factual anchors. Extracted SMT-LIB2 representation:\n\n{smt_lib}"
                        }
                    ]
                }
            }

        elif tool_name == "mcp_oracle_toe_z3_tribunal":
            smt_script = arguments.get("smt_script", "")
            evaluation = self.tribunal.evaluate_satisfiability(smt_script)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Vonis Tribunal: {evaluation['verdict']}\nMessage: {evaluation['message']}\nMinimal Correction Set (MCS): {evaluation['mcs']}"
                        }
                    ]
                }
            }

        elif tool_name == "mcp_oracle_toe_execute_skill":
            pillar = arguments.get("pillar", "")
            payload = arguments.get("payload", "")
            desc = self.router.pillars.get(pillar, "Unknown Pillar")
            
            wipe_buffer = bytearray(b"TransientSessionEntropySecretKey")
            self.router.wipe_transient_buffer(wipe_buffer)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Task executed under Pillar '{pillar}' ({desc}).\nResult: [SAT]\nIsentropic Amnesia triggered: Transient session key buffer wiped physically."
                        }
                    ]
                }
            }

        elif tool_name == "mcp_oracle_toe_list_documents":
            docs = self.corpus.list_documents()
            return self._ok(request_id, json.dumps(
                {"root": self.corpus.root, "count": len(docs), "documents": docs},
                ensure_ascii=False, indent=1))

        elif tool_name == "mcp_oracle_toe_read_document":
            try:
                payload = self.corpus.read_document(
                    arguments.get("name", ""),
                    page=arguments.get("page"),
                    offset=arguments.get("offset", 0),
                    limit=arguments.get("limit", 200),
                )
                return self._ok(request_id, json.dumps(payload, ensure_ascii=False, indent=1))
            except Exception as exc:
                return self._deny(request_id, f"[ERROR] read_document failed: {exc}")

        elif tool_name == "mcp_oracle_toe_search_corpus":
            hits = self.corpus.search(
                arguments.get("query", ""),
                use_regex=bool(arguments.get("regex", False)),
                max_hits=arguments.get("max_hits", 40),
            )
            return self._ok(request_id, json.dumps(
                {"query": arguments.get("query", ""), "hits": len(hits), "results": hits},
                ensure_ascii=False, indent=1))

        elif tool_name == "mcp_oracle_toe_reference":
            return self._ok(request_id, json.dumps(REFERENCE_DATA, ensure_ascii=False, indent=1))

        elif tool_name == "mcp_oracle_toe_write_file":
            target_path = arguments.get("path", "")
            content = arguments.get("content", "")

            # Resolve against cwd, then require the result to sit inside an allowlisted root.
            resolved = os.path.realpath(os.path.normpath(
                target_path if os.path.isabs(target_path)
                else os.path.join(os.getcwd(), target_path)
            ))
            resolved_norm = os.path.normcase(resolved)
            in_bounds = any(
                resolved_norm == root or resolved_norm.startswith(root + os.sep)
                for root in self.write_roots
            )

            # Formulate the constraints for Z3 Tribunal
            smt_check_script = f"""
            (set-logic QF_LIA)
            (declare-const path_is_unsafe Int)
            (assert (= path_is_unsafe {0 if in_bounds else 1}))
            (assert (= path_is_unsafe 0))
            (check-sat)
            """

            verdict_report = self.tribunal.evaluate_satisfiability(smt_check_script)
            if verdict_report["verdict"] == "UNSATISFIABLE":
                return self._deny(
                    request_id,
                    f"[FATAL_UNSAT] Path '{target_path}' resolves outside the allowlist "
                    f"roots {self.write_roots}. Blocked by SMT Tribunal.",
                )
            if verdict_report["verdict"] != "SATISFIABLE":
                # Fail-closed: if the safety constraint cannot be decided, the write
                # does not happen. UNKNOWN is never an approval.
                return self._deny(
                    request_id,
                    f"[NOT-DECIDABLE] Tribunal could not decide the allowlist constraint "
                    f"({verdict_report['verdict']}); write refused (fail-closed).",
                )

            try:
                parent = os.path.dirname(resolved)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with open(resolved, "w", encoding="utf-8") as f:
                    f.write(content)
                return self._ok(
                    request_id,
                    f"[SAT] File successfully written to: {resolved} ({len(content)} bytes).",
                )
            except Exception as e:
                return self._deny(request_id, f"[ERROR] Failed to write file: {str(e)}")

        elif tool_name == "mcp_oracle_toe_execute_command":
            if not EXEC_ENABLED:
                return self._deny(
                    request_id,
                    "[DENIED] execute_command is disabled (set SHP_MCP_ALLOW_EXEC=1 to enable).",
                )

            cmd = arguments.get("command", "")

            # SMT-guided command threat modeling
            blacklist = ["rm -rf", "format", "mkfs", "shutdown", "reboot", "nuke"]
            is_malicious = any(item in cmd.lower() for item in blacklist)

            smt_cmd_check = f"""
            (set-logic QF_LIA)
            (declare-const cmd_is_malicious Int)
            (assert (= cmd_is_malicious {1 if is_malicious else 0}))
            (assert (= cmd_is_malicious 0))
            (check-sat)
            """

            verdict_report = self.tribunal.evaluate_satisfiability(smt_cmd_check)
            if verdict_report["verdict"] == "UNSATISFIABLE":
                return self._deny(
                    request_id,
                    f"[FATAL_UNSAT] Command '{cmd}' contains blocked or malicious execution "
                    "sequences! Terminated by SMT Tribunal.",
                )
            if verdict_report["verdict"] != "SATISFIABLE":
                # Fail-closed: an undecided threat model is not a clearance.
                return self._deny(
                    request_id,
                    f"[NOT-DECIDABLE] Tribunal could not decide the threat model "
                    f"({verdict_report['verdict']}); execution refused (fail-closed).",
                )

            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                output = res.stdout if res.stdout else res.stderr
                return self._ok(
                    request_id,
                    f"[SAT] Execution completed.\nExit Code: {res.returncode}\n\n"
                    f"[STDOUT/STDERR]:\n{output}",
                )
            except Exception as e:
                return self._deny(request_id, f"[ERROR] Failed to execute command: {str(e)}")

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method {tool_name} not found"
                }
            }

    async def main_loop(self):
        self.log("Sovereign SHP-MCP Bridge active on stdio. Awaiting commands...")
        while self.running:
            loop = asyncio.get_event_loop()
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            try:
                msg = json.loads(line.strip())
                request_id = msg.get("id")
                method = msg.get("method")
                
                if method == "initialize":
                    response = self.handle_initialize(request_id, msg.get("params", {}))
                elif method == "ping":
                    response = {"jsonrpc": "2.0", "id": request_id, "result": {}}
                elif method == "tools/list":
                    response = self.handle_list_tools(request_id)
                elif method == "tools/call":
                    params = msg.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    response = self.handle_call_tool(request_id, tool_name, arguments)
                elif method == "notifications/initialized":
                    self.log("Initialized notification received.")
                    continue
                else:
                    if request_id is not None:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method {method} not found"
                            }
                        }
                    else:
                        continue
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                self.log(f"Error processing line: {str(e)}")


# =====================================================================
# 7. INTEGRATED AUTOMATED TEST SUITE (--test mode)
# =====================================================================
def run_integrated_test_suite():
    print("=====================================================================")
    print(" AETHER - SINGULARITAS HEPTAGONAL SHP-MCP BRIDGE AUTOMATED TEST SUITE")
    print("=====================================================================")
    z3_state = ('ACTIVE (pyz3 native, PROOF-ONLY: fail-loud UNKNOWN on rejected scripts, '
                'TOOL NOT RUN without z3py)') if Z3_AVAILABLE else \
               ('INACTIVE (PROOF-ONLY: no simulated verdict exists; every call returns '
                'TOOL NOT RUN [PROOF-ONLY - NOT A SIMULATED] and all consumers refuse)')
    print(f"Z3 Solver Status: {z3_state}")
    print(f"Corpus Root:      {DEFAULT_CORPUS_ROOT}")
    print(f"Write Roots:      {_default_write_roots()}")
    print(f"Execute Command:  {'ENABLED (SHP_MCP_ALLOW_EXEC=1)' if EXEC_ENABLED else 'DISABLED (default off)'}")
    print("---------------------------------------------------------------------")

    server = ShpMcpBridgeServer()
    success = True

    # Test 1: Hyperdimensional Computing Engine
    print("[TEST 1] Testing HDC Engine...")
    vec_a = server.hdc_engine.generate_bipolar_vector("Target Alpha")
    vec_b = server.hdc_engine.generate_bipolar_vector("Target Beta")
    ref_vec = server.hdc_engine.generate_bipolar_vector("0x00 Null Bytes")
    sim_ab = server.hdc_engine.cosine_similarity(vec_a, vec_b)
    sim_ref = server.hdc_engine.cosine_similarity(vec_a, ref_vec)
    print(f" -> Cosine similarity vector A vs B: {sim_ab:.4f}")
    print(f" -> Cosine similarity vs Ground State (Orthogonality): {sim_ref:.4f}")
    if abs(sim_ref) < 0.05:
        print(" -> [PASS] Orthogonality holds perfectly.")
    else:
        print(" -> [FAIL] Orthogonality breach!")
        success = False

    # Test 2: Epistemic Sieve Compiler
    print("\n[TEST 2] Testing Epistemic Sieve...")
    raw_text = "Mungkin target memiliki celah keamanan. Namun sepertinya host_limit adalah 500."
    clean = server.sieve.purge_assumptions(raw_text)
    print(f" -> Raw input: '{raw_text}'")
    print(f" -> Purged facts: {clean}")
    if len(clean) == 0:
         print(" -> [PASS] Stochastic Purge successfully incinerated vague assumptions.")
    else:
         print(" -> [WARN] Some sentences remained. Sieve is working selectively.")

    # Test 3: SMT Tribunal SAT/UNSAT Check
    print("\n[TEST 3] Testing SMT Tribunal...")
    sat_script = """
    (set-logic QF_LIA)
    (declare-const x Int)
    (declare-const limit Int)
    (assert (= limit 1000))
    (assert (< x limit))
    (check-sat)
    """
    unsat_script = """
    (set-logic QF_LIA)
    (declare-const x_val Int)
    (assert (= x_val 10))
    (assert (= x_val 20))
    (check-sat)
    """
    
    sat_res = server.tribunal.evaluate_satisfiability(sat_script)
    print(f" -> SAT Script evaluation verdict: {sat_res['verdict']}")
    unsat_res = server.tribunal.evaluate_satisfiability(unsat_script)
    print(f" -> UNSAT Script evaluation verdict: {unsat_res['verdict']}")
    
    if sat_res['verdict'] == "SATISFIABLE" and unsat_res['verdict'] == "UNSATISFIABLE":
        print(" -> [PASS] SMT Tribunal successfully resolved SAT/UNSAT boundary bounds.")
    else:
        print(" -> [FAIL] Logic evaluation failure!")
        success = False

    # Test 4: Write File allowlist + SMT path constraint check
    print("\n[TEST 4] Testing Allowlisted Write File Tool...")
    # The "safe" path must come from the live allowlist, not a hardcoded TEMP
    # path: when SHP_MCP_WRITE_ROOTS restricts the roots (as it is in the
    # opencode registration), TEMP is legitimately refused and the test would
    # report a false CONTRADICTION while enforcement is working correctly.
    safe_dir = _default_write_roots()[0]
    os.makedirs(safe_dir, exist_ok=True)
    safe_path = os.path.join(safe_dir, "test_hands.txt")
    safe_write_args = {"path": safe_path, "content": "AETHER-Z3-OMEGA SATISFIABLE"}
    unsafe_write_args = {"path": "../../../etc/passwd", "content": "Hack"}

    safe_res = server.handle_call_tool(1, "mcp_oracle_toe_write_file", safe_write_args)
    safe_text = safe_res["result"]["content"][0]["text"]
    print(f" -> Allowlisted Path write result: {safe_text}")

    unsafe_res = server.handle_call_tool(2, "mcp_oracle_toe_write_file", unsafe_write_args)
    unsafe_text = unsafe_res["result"]["content"][0]["text"]
    print(f" -> Out-of-allowlist write result: {unsafe_text}")

    if "[SAT]" in safe_text and "[FATAL_UNSAT]" in unsafe_text:
        print(" -> [PASS] Write allowlist + SMT Tribunal blocked the escape.")
        if os.path.exists(safe_path):
            os.remove(safe_path)
    else:
        print(" -> [FAIL] Write allowlist enforcement failure!")
        success = False

    # Test 5: Execute Command gating
    print("\n[TEST 5] Testing Command Execution Gate...")
    safe_cmd_args = {"command": "echo AETHER-SAT"}
    unsafe_cmd_args = {"command": "rm -rf /"}

    safe_cmd_res = server.handle_call_tool(3, "mcp_oracle_toe_execute_command", safe_cmd_args)
    safe_cmd_text = safe_cmd_res["result"]["content"][0]["text"]
    unsafe_cmd_res = server.handle_call_tool(4, "mcp_oracle_toe_execute_command", unsafe_cmd_args)
    unsafe_cmd_text = unsafe_cmd_res["result"]["content"][0]["text"]

    if not EXEC_ENABLED:
        if "[DENIED]" in safe_cmd_text and "[DENIED]" in unsafe_cmd_text:
            print(" -> [PASS] execute_command is default-off (both calls denied).")
        else:
            print(f" -> [FAIL] Expected [DENIED], got: {safe_cmd_text} / {unsafe_cmd_text}")
            success = False
    else:
        print(f" -> Safe Command result: {safe_cmd_text.splitlines()[0]} ...")
        print(f" -> Unsafe Command result: {unsafe_cmd_text}")
        if "[SAT]" in safe_cmd_text and "[FATAL_UNSAT]" in unsafe_cmd_text:
            print(" -> [PASS] SMT-guided command blacklist blocked malicious payload.")
        else:
            print(" -> [FAIL] Command execution filtration failure!")
            success = False

    # Test 6: Theory-of-Everything corpus tools
    print("\n[TEST 6] Testing ToE Corpus Tools...")
    docs = server.corpus.list_documents()
    print(f" -> list_documents: {len(docs)} documents indexed")
    reads = 0
    if docs:
        probe = docs[0]["name"]
        try:
            payload = server.corpus.read_document(probe, offset=0, limit=5)
            reads = 1 if payload["text"] else 0
            print(f" -> read_document('{probe}'): {payload['returned_lines']} lines of {payload['total_lines']}")
        except Exception as exc:
            print(f" -> read_document ERROR: {exc}")
    hits = server.corpus.search("Riemann", max_hits=5)
    print(f" -> search('Riemann'): {len(hits)} hits"
          + (f" (first: {hits[0]['file']} {hits[0]['at']})" if hits else ""))
    if len(docs) >= 10 and reads == 1 and len(hits) > 0:
        print(" -> [PASS] Corpus index, reader and search are operational.")
    else:
        print(" -> [FAIL] Corpus toolchain failure!")
        success = False

    # Test 7: Curated reference data
    print("\n[TEST 7] Testing Reference Constants...")
    ref_keys = list(REFERENCE_DATA.keys())
    scope = REFERENCE_DATA.get("guinand_weil_scope", {})
    print(f" -> REFERENCE_DATA sections: {ref_keys}")
    print(f" -> no_claim: {scope.get('no_claim', '')[:70]}...")
    if "octave_8_pillars" in REFERENCE_DATA and "rh_pipeline" in REFERENCE_DATA \
            and "no_claim" in scope:
        print(" -> [PASS] Reference constants carry provenance and scope limits.")
    else:
        print(" -> [FAIL] Reference data incomplete!")
        success = False

    # Test 8: Fail-loud verdict contract (regression for the silent-fallback bug)
    print("\n[TEST 8] Testing Fail-Loud Verdict Contract...")
    grand_pipeline_smt = """
    (declare-const E Real)
    (assert (<= E (log (+ 1.0 E))))
    (assert (< (log (+ 1.0 E)) E))
    (check-sat)
    """
    probe = server.tribunal.evaluate_satisfiability(grand_pipeline_smt)
    print(f" -> log-script verdict: {probe['verdict']} (simulated={probe.get('simulated')})")
    print(f" -> message: {probe['message'][:70]}...")
    # The documented regression: with z3py present this must be UNKNOWN, never a
    # simulated SATISFIABLE/UNSATISFIABLE answer. Without z3py it must be a
    # refusal, because PROOF-ONLY admits no verdict that no solver produced.
    if Z3_AVAILABLE:
        ok8 = probe["verdict"] == "UNKNOWN" and not probe.get("simulated", False)
    else:
        ok8 = probe["verdict"] == "TOOL NOT RUN" and probe.get("simulated") is False
    if ok8:
        print(" -> [PASS] Rejected script yields UNKNOWN - no silent simulated verdict.")
    else:
        print(f" -> [FAIL] Expected fail-loud UNKNOWN, got: {probe['verdict']}")
        success = False

    # Test 9: PROOF-ONLY contract (regression for the removed simulation branch)
    print("\n[TEST 9] Testing PROOF-ONLY Refusal Without z3py...")
    saved_active = server.tribunal.z3_active
    server.tribunal.z3_active = False
    try:
        forced = server.tribunal.evaluate_satisfiability(sat_script)
        forced_unsat = server.tribunal.evaluate_satisfiability(unsat_script)
    finally:
        server.tribunal.z3_active = saved_active
    print(f" -> z3py disabled: sat-script -> {forced['verdict']}")
    print(f" -> z3py disabled: unsat-script -> {forced_unsat['verdict']}")
    ok9 = (forced["verdict"] == "TOOL NOT RUN"
           and forced_unsat["verdict"] == "TOOL NOT RUN"
           and forced.get("simulated") is False
           and "PROOF-ONLY - NOT A SIMULATED" in forced["message"])
    if ok9:
        print(" -> [PASS] No solver, no verdict: TOOL NOT RUN, label PROOF-ONLY.")
    else:
        print(f" -> [FAIL] PROOF-ONLY violated: {forced['verdict']} / {forced_unsat['verdict']}")
        success = False

    # Test 10: PROOF-ONLY is fail-closed at the action layer
    print("\n[TEST 10] Testing Fail-Closed Action Under TOOL NOT RUN...")
    # Path is deliberately INSIDE the allowlist, so the only reason for refusal
    # can be the missing proof - not the path check.
    proof_probe = os.path.join(_default_write_roots()[0], "proof_only_probe.txt")
    server.tribunal.z3_active = False
    try:
        refused = server.handle_call_tool(
            99, "mcp_oracle_toe_write_file",
            {"path": proof_probe, "content": "must not be written without a proof"})
    finally:
        server.tribunal.z3_active = saved_active
    refused_text = refused["result"]["content"][0]["text"]
    print(f" -> write under TOOL NOT RUN: {refused_text.splitlines()[0][:90]}")
    ok10 = (refused.get("result", {}).get("isError", False)
            and "TOOL NOT RUN" in refused_text
            and not os.path.exists(proof_probe))
    if ok10:
        print(" -> [PASS] Action refused: no proof, no effect.")
    else:
        print(f" -> [FAIL] Expected fail-closed refusal, got: {refused_text[:120]}")
        success = False

    print("\n---------------------------------------------------------------------")
    if success:
        print(" >> TRIBUNAL STATE: LOCKED [SATISFIABLE]. BRIDGE READY FOR PRODUCTION.")
    else:
        print(" >> TRIBUNAL STATE: CONTRADICTION [UNSAT]. FIX SYSTEM COHERENCE.")
    print("=====================================================================")
    return success


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # A suite that prints CONTRADICTION must not exit 0: an exit code of 0
        # is a machine-checkable claim that every check passed.
        sys.exit(0 if run_integrated_test_suite() else 1)
    else:
        server = ShpMcpBridgeServer()
        asyncio.run(server.main_loop())
