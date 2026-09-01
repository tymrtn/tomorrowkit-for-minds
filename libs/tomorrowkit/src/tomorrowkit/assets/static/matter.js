/* Tomorrowkit matter workspace.
   One in-memory document, edited in place, autosaved (debounced) via PUT.
   All URLs are relative; the page's <base href="../"> points at the app root. */

(function () {
  "use strict";

  var MATTER_ID = document.body.dataset.matterId;
  var API_URL = "api/matters/" + MATTER_ID;

  var STAGE_LABELS = {
    EARLY_IDEA: "Early idea",
    DRAFT_READY: "Draft-ready",
    FILED_PROVISIONAL: "Filed provisional",
    EXISTING_APPLICATION: "Existing application"
  };
  var SOURCE_TYPE_LABELS = {
    PATENT_PUBLICATION: "Patent publication",
    PAPER: "Paper",
    PRODUCT: "Product",
    WEB_PAGE: "Web page",
    STANDARD: "Standard",
    INVENTOR_MATERIAL: "Inventor material",
    RESEARCH_LEAD: "Research lead"
  };
  var RELATIONSHIP_LABELS = {
    SUPPORTS: "Supports",
    CONTRADICTS: "Contradicts",
    DESIGN_AROUND: "Design-around",
    SEARCH_LEAD: "Search lead",
    NEEDS_VERIFICATION: "Needs verification"
  };
  var VERIFICATION_LABELS = { LEAD: "Lead", REVIEWED: "Reviewed", VERIFIED: "Verified" };
  var DECISION_KIND_LABELS = {
    COMMERCIAL_TERRAIN: "Commercial terrain",
    EMBODIMENT_CHOICE: "Embodiment choice",
    DEFERRAL: "Deferral",
    SUGGESTION_DISPOSITION: "Suggestion disposition",
    OTHER: "Other"
  };
  var NODE_KIND_LABELS = {
    COMPONENT: "Component",
    ACTOR: "Actor",
    INPUT: "Input",
    OUTPUT: "Output",
    STEP: "Step",
    ALTERNATIVE: "Alternative",
    QUESTION: "Question",
    ASSUMPTION: "Assumption",
    EVIDENCE: "Evidence"
  };
  var WORKFLOW_PHASES = [
    { key: "orient", label: "Orient", phases: ["WELCOME", "TRIAGE_QUIZ"] },
    { key: "frame", label: "Frame the invention", phases: ["SOURCE_LOCK", "OBJECTIVE_LOCK", "CORE_MECHANISM"] },
    { key: "explore", label: "Explore the terrain", phases: ["SEED_EXPANSION", "SEED_ASSAY", "TERRAIN_SELECTION"] },
    { key: "build", label: "Build the disclosure", phases: ["PROVISIONAL_POSTURE", "DISCLOSURE_BUILD"] },
    { key: "harden", label: "Harden and hand off", phases: ["ATTACK_REPAIR", "READY_HANDOFF"] }
  ];
  var WORKFLOW_PHASE_LABELS = {
    WELCOME: "Welcome",
    TRIAGE_QUIZ: "Orientation",
    SOURCE_LOCK: "Lock source facts",
    OBJECTIVE_LOCK: "Define the objective",
    CORE_MECHANISM: "Describe the core mechanism",
    SEED_EXPANSION: "Expand possible invention seeds",
    SEED_ASSAY: "Test the strongest seeds",
    TERRAIN_SELECTION: "Choose the terrain",
    PROVISIONAL_POSTURE: "Set the provisional posture",
    DISCLOSURE_BUILD: "Build the disclosure",
    ATTACK_REPAIR: "Attack and repair the record",
    READY_HANDOFF: "Prepare the handoff"
  };

  // Per-matter accent themes. The empty slug is the default drafting blue
  // already declared in the stylesheet; unknown slugs (e.g. free-text themes
  // from older matters) also fall back to it.
  var THEME_ACCENTS = {
    "field-green": { accent: "#3f6d4e", soft: "#dfe9dc" },
    "kiln-amber": { accent: "#7a5424", soft: "#efe5cb" },
    "ink-violet": { accent: "#5b4a7d", soft: "#e4dfec" },
    "harbor-teal": { accent: "#2f6b68", soft: "#dcebe8" }
  };

  function applyTheme() {
    var rootStyle = document.documentElement.style;
    var theme = THEME_ACCENTS[doc.theme];
    if (theme) {
      rootStyle.setProperty("--draft", theme.accent);
      rootStyle.setProperty("--draft-soft", theme.soft);
    } else {
      rootStyle.removeProperty("--draft");
      rootStyle.removeProperty("--draft-soft");
    }
  }

  var doc = null;
  var saveTimer = null;
  var retryTimer = null;
  var pollTimer = null;
  var isSaving = false;
  var isDirtyWhileSaving = false;
  var hasUnsavedChanges = false;
  var editGeneration = 0;
  var pendingRemoteDoc = null;

  function $(id) { return document.getElementById(id); }

  function escapeHtml(text) {
    return String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function randomHex32() {
    var bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    return Array.prototype.map.call(bytes, function (b) {
      return ("0" + b.toString(16)).slice(-2);
    }).join("");
  }

  /* ---------- saving ---------- */

  function setSaveStatus(text, isError) {
    var el = $("save-status");
    el.textContent = text;
    el.classList.toggle("error", Boolean(isError));
  }

  function scheduleSave() {
    if (saveTimer) { clearTimeout(saveTimer); }
    editGeneration += 1;
    hasUnsavedChanges = true;
    setSaveStatus("Editing…");
    saveTimer = setTimeout(saveNow, 900);
  }

  function saveNow() {
    if (isSaving) { isDirtyWhileSaving = true; return; }
    if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
    isSaving = true;
    var requestGeneration = editGeneration;
    setSaveStatus("Saving…");
    fetch(API_URL, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(doc)
    }).then(function (response) {
      if (response.status === 409) {
        var conflict = new Error("matter changed in another session");
        conflict.isConflict = true;
        throw conflict;
      }
      if (!response.ok) { throw new Error("save failed (" + response.status + ")"); }
      return response.json();
    }).then(function (saved) {
      isSaving = false;
      if (editGeneration !== requestGeneration) {
        // Keep the live document: it contains edits made after this request's
        // snapshot. Only advance its optimistic-lock revision, then persist
        // those newer edits in a follow-up request.
        doc.updated_at = saved.updated_at;
        isDirtyWhileSaving = false;
        saveNow();
        return;
      }
      doc = saved;
      isDirtyWhileSaving = false;
      hasUnsavedChanges = false;
      pendingRemoteDoc = null;
      hideSyncNotice();
      renderCurrentRecord();
      var when = new Date(saved.updated_at);
      setSaveStatus("Saved " + when.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }).catch(function (error) {
      isSaving = false;
      if (error.isConflict) {
        setSaveStatus("The agent has a newer version — review before saving", true);
        fetchRemoteDocument(true);
        return;
      }
      setSaveStatus("Not saved — retrying shortly", true);
      if (retryTimer) { clearTimeout(retryTimer); }
      retryTimer = setTimeout(saveNow, 4000);
    });
  }

  /* ---------- live record and companion view ---------- */

  function textOrFallback(value, fallback) {
    return value && String(value).trim() ? String(value).trim() : fallback;
  }

  function inferredWorkflowPhase() {
    if (doc.workflow_phase) { return doc.workflow_phase; }
    var checkpoints = doc.harvest || [];
    var captured = checkpoints.filter(function (checkpoint) { return checkpoint.status === "CAPTURED"; });
    var inProgress = checkpoints.find(function (checkpoint) { return checkpoint.status === "IN_PROGRESS"; });
    if (inProgress && inProgress.checkpoint_id === "adversarial") { return "ATTACK_REPAIR"; }
    if (inProgress && inProgress.checkpoint_id === "drafting") { return "DISCLOSURE_BUILD"; }
    if (inProgress && inProgress.checkpoint_id === "prospecting") { return "SEED_ASSAY"; }
    if (captured.length >= checkpoints.length && checkpoints.length) { return "READY_HANDOFF"; }
    if (captured.length >= 3) { return "ATTACK_REPAIR"; }
    if (captured.length >= 2) { return "DISCLOSURE_BUILD"; }
    if (captured.length >= 1) { return "SEED_EXPANSION"; }
    return "SOURCE_LOCK";
  }

  function workflowGroupIndex(phase) {
    var index = WORKFLOW_PHASES.findIndex(function (group) {
      return group.phases.indexOf(phase) !== -1;
    });
    return index === -1 ? 1 : index;
  }

  function renderProgressRail() {
    var phase = inferredWorkflowPhase();
    var activeIndex = workflowGroupIndex(phase);
    $("phase-focus").textContent = WORKFLOW_PHASE_LABELS[phase] || "Develop the record";
    $("progress-rail").innerHTML = WORKFLOW_PHASES.map(function (group, index) {
      var state = index < activeIndex ? "complete" : (index === activeIndex ? "active" : "upcoming");
      var stateLabel = state === "complete" ? "Complete" : (state === "active" ? "Current" : "Later");
      return '<li class="' + state + '"' + (state === "active" ? ' aria-current="step"' : "") + '>' +
        '<span class="rail-marker" aria-hidden="true"></span>' +
        '<span><strong>' + escapeHtml(group.label) + '</strong><small>' + stateLabel + "</small></span>" +
      "</li>";
    }).join("");
  }

  function renderContinue() {
    var brief = doc.brief || {};
    var briefFields = [brief.problem, brief.mechanism, brief.intended_result, brief.alternatives, brief.open_questions];
    var briefCount = briefFields.filter(function (value) { return value && String(value).trim(); }).length;
    var updated = new Date(doc.updated_at);
    $("continue-stage").textContent = STAGE_LABELS[doc.stage] || String(doc.stage || "In progress").replace(/_/g, " ");
    $("continue-updated").textContent = "Record refreshed " + updated.toLocaleString([], {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
    });
    $("continue-next").textContent = textOrFallback(
      doc.next_action,
      "Tell Tomorrowkit you are ready to continue. It will begin by confirming the source material and the facts that need dates."
    );
    $("continue-known").textContent = textOrFallback(
      doc.what_is_known,
      textOrFallback(brief.problem, textOrFallback(doc.problem_summary, "The orientation is complete. The invention itself has not been described yet."))
    );
    $("continue-uncertain").textContent = textOrFallback(
      doc.what_is_uncertain,
      textOrFallback(brief.open_questions, "Tomorrowkit will keep assumptions, missing dates, and unverified technical details visible as they emerge.")
    );
    $("artifact-brief-summary").textContent = textOrFallback(
      brief.mechanism,
      textOrFallback(brief.problem, "The conversation will turn your explanation into a structured brief.")
    );
    $("artifact-brief-count").textContent = briefCount + " of 5 sections captured";
    $("artifact-map-count").textContent = (doc.map_nodes || []).length + " elements · " + (doc.map_edges || []).length + " connections";
    $("artifact-reference-count").textContent = (doc.references || []).length + " sources in the record";
    $("artifact-decision-count").textContent = (doc.decisions || []).length + " decisions recorded";
    renderProgressRail();
  }

  function editableControlHasFocus() {
    var active = document.activeElement;
    return Boolean(active && active.closest && active.closest("main") && active.matches("input, textarea, select"));
  }

  function hasPendingLocalWork() {
    return hasUnsavedChanges || isSaving || isDirtyWhileSaving || Boolean(saveTimer) || editableControlHasFocus();
  }

  function showSyncNotice() {
    $("sync-notice").hidden = false;
  }

  function hideSyncNotice() {
    $("sync-notice").hidden = true;
  }

  function setControlValue(id, value) {
    var control = $(id);
    if (control) { control.value = value == null ? "" : value; }
  }

  function renderReviewFields() {
    setControlValue("f-title", doc.title);
    setControlValue("f-stage", doc.stage);
    setControlValue("f-goal", doc.goal);
    setControlValue("f-problem", doc.problem_summary);
    setControlValue("f-known", doc.what_is_known);
    setControlValue("f-uncertain", doc.what_is_uncertain);
    setControlValue("f-next", doc.next_action);
    setControlValue("f-theme", THEME_ACCENTS[doc.theme] ? doc.theme : "");
    setControlValue("b-problem", doc.brief.problem);
    setControlValue("b-mechanism", doc.brief.mechanism);
    setControlValue("b-result", doc.brief.intended_result);
    setControlValue("b-alternatives", doc.brief.alternatives);
    setControlValue("b-questions", doc.brief.open_questions);
    renderDates();
    renderScorecard();
  }

  function renderCurrentRecord() {
    applyTheme();
    renderSidebar();
    renderContinue();
    renderReviewFields();
    renderLibrary();
    renderLedger();
    refreshNodeReferenceOptions();
    renderMap();
  }

  function applyRemoteDocument(remote) {
    doc = remote;
    pendingRemoteDoc = null;
    hasUnsavedChanges = false;
    isDirtyWhileSaving = false;
    hideSyncNotice();
    renderCurrentRecord();
    setSaveStatus("Updated by Tomorrowkit " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  }

  function fetchRemoteDocument(forceNotice) {
    fetch(API_URL, { cache: "no-store" }).then(function (response) {
      if (!response.ok) { throw new Error("refresh failed (" + response.status + ")"); }
      return response.json();
    }).then(function (remote) {
      if (!doc || remote.updated_at === doc.updated_at) { return; }
      if (forceNotice || hasPendingLocalWork()) {
        pendingRemoteDoc = remote;
        showSyncNotice();
        return;
      }
      applyRemoteDocument(remote);
    }).catch(function () {
      // The loaded record remains usable. The next polling interval tries again.
    });
  }

  function startPolling() {
    pollTimer = window.setInterval(function () {
      if (!document.hidden) { fetchRemoteDocument(false); }
    }, 2500);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) { fetchRemoteDocument(false); }
    });
  }

  /* ---------- sidebar ---------- */

  function renderSidebar() {
    $("side-title").textContent = doc.title;
    $("side-stamp").textContent = STAGE_LABELS[doc.stage] || doc.stage;
    $("side-matter-no").textContent = doc.matter_id.slice(-8).toUpperCase();
    document.title = doc.title + " — Tomorrowkit";
    $("count-map").textContent = String(doc.map_nodes.length || "");
    $("count-library").textContent = String(doc.references.length || "");
    $("count-ledger").textContent = String(doc.decisions.length || "");
  }

  /* ---------- pane switching ---------- */

  function openPane(paneName) {
    document.querySelectorAll("#side-nav button").forEach(function (button) {
      button.classList.toggle("active", button.dataset.pane === paneName);
    });
    document.querySelectorAll(".pane").forEach(function (pane) { pane.classList.remove("active"); });
    var pane = $("pane-" + paneName);
    if (pane) {
      pane.classList.add("active");
      pane.focus({ preventScroll: true });
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  function initNav() {
    $("side-nav").addEventListener("click", function (event) {
      var button = event.target.closest("button[data-pane]");
      if (!button) { return; }
      openPane(button.dataset.pane);
    });
    document.addEventListener("click", function (event) {
      var button = event.target.closest("[data-open-pane]");
      if (!button) { return; }
      openPane(button.dataset.openPane);
    });
  }

  /* ---------- simple field bindings ---------- */

  function bindInput(id, getValue, setValue, extraOnInput) {
    var el = $(id);
    el.value = getValue();
    el.addEventListener("input", function () {
      setValue(el.value);
      if (extraOnInput) { extraOnInput(); }
      scheduleSave();
    });
  }

  function initHomePane() {
    bindInput("f-title", function () { return doc.title; }, function (v) { doc.title = v; }, renderSidebar);
    bindInput("f-stage", function () { return doc.stage; }, function (v) { doc.stage = v; }, renderSidebar);
    bindInput("f-goal", function () { return doc.goal; }, function (v) { doc.goal = v; });
    bindInput("f-problem", function () { return doc.problem_summary; }, function (v) { doc.problem_summary = v; });
    bindInput("f-known", function () { return doc.what_is_known; }, function (v) { doc.what_is_known = v; });
    bindInput("f-uncertain", function () { return doc.what_is_uncertain; }, function (v) { doc.what_is_uncertain = v; });
    bindInput("f-next", function () { return doc.next_action; }, function (v) { doc.next_action = v; });
    var themeSelect = $("f-theme");
    themeSelect.value = THEME_ACCENTS[doc.theme] ? doc.theme : "";
    themeSelect.addEventListener("change", function () {
      doc.theme = themeSelect.value;
      applyTheme();
      scheduleSave();
    });
    $("add-date").addEventListener("click", function () {
      doc.known_dates.push({ label: "", date_text: "", note: "" });
      renderDates();
      scheduleSave();
    });
    renderDates();
  }

  function renderDates() {
    var list = $("dates-list");
    list.innerHTML = "";
    if (!doc.known_dates.length) {
      list.innerHTML = '<div class="empty-note">No dates yet. If you have shown, sold, published, or filed anything, those dates belong here.</div>';
      return;
    }
    doc.known_dates.forEach(function (entry, index) {
      var row = document.createElement("div");
      row.className = "date-row";
      row.innerHTML =
        '<input type="text" placeholder="What happened" value="' + escapeHtml(entry.label) + '" data-role="label">' +
        '<input type="text" placeholder="When" value="' + escapeHtml(entry.date_text) + '" data-role="date" class="mono">' +
        '<input type="text" placeholder="Note (optional)" value="' + escapeHtml(entry.note) + '" data-role="note">' +
        '<button type="button" class="btn tiny" data-role="remove">Remove</button>';
      row.querySelector('[data-role="label"]').addEventListener("input", function (e) { entry.label = e.target.value; scheduleSave(); });
      row.querySelector('[data-role="date"]').addEventListener("input", function (e) { entry.date_text = e.target.value; scheduleSave(); });
      row.querySelector('[data-role="note"]').addEventListener("input", function (e) { entry.note = e.target.value; scheduleSave(); });
      row.querySelector('[data-role="remove"]').addEventListener("click", function () {
        doc.known_dates.splice(index, 1);
        renderDates();
        scheduleSave();
      });
      list.appendChild(row);
    });
  }

  /* ---------- brief ---------- */

  function initBriefPane() {
    bindInput("b-problem", function () { return doc.brief.problem; }, function (v) { doc.brief.problem = v; });
    bindInput("b-mechanism", function () { return doc.brief.mechanism; }, function (v) { doc.brief.mechanism = v; });
    bindInput("b-result", function () { return doc.brief.intended_result; }, function (v) { doc.brief.intended_result = v; });
    bindInput("b-alternatives", function () { return doc.brief.alternatives; }, function (v) { doc.brief.alternatives = v; });
    bindInput("b-questions", function () { return doc.brief.open_questions; }, function (v) { doc.brief.open_questions = v; });
  }

  /* ---------- harvest ---------- */

  function renderHarvest() {
    renderProgressRail();
  }

  /* ---------- reference library ---------- */

  var libraryEditingId = null;

  function initLibraryPane() {
    $("lib-add").addEventListener("click", function () { openLibraryEditor(null); });
    $("le-cancel").addEventListener("click", function () { closeLibraryEditor(); });
    $("le-save").addEventListener("click", saveLibraryEntry);
    $("lib-filter").addEventListener("input", renderLibrary);
  }

  function openLibraryEditor(referenceId) {
    libraryEditingId = referenceId;
    var entry = doc.references.find(function (r) { return r.reference_id === referenceId; }) || null;
    $("lib-editor-title").textContent = entry ? "Edit entry" : "New entry";
    $("le-title").value = entry ? entry.title : "";
    $("le-citation").value = entry ? entry.citation : "";
    $("le-source-type").value = entry ? entry.source_type : "RESEARCH_LEAD";
    $("le-relationship").value = entry ? entry.relationship : "NEEDS_VERIFICATION";
    $("le-relevance").value = entry ? entry.relevance_note : "";
    $("le-tags").value = entry ? entry.tags.join(", ") : "";
    $("le-date").value = entry ? entry.source_date_text : "";
    $("le-provenance").value = entry ? entry.provenance_note : "";
    $("le-verification").value = entry ? entry.verification_state : "LEAD";
    $("le-error").textContent = "";
    $("lib-editor").hidden = false;
    $("le-title").focus();
  }

  function closeLibraryEditor() {
    libraryEditingId = null;
    $("lib-editor").hidden = true;
  }

  function saveLibraryEntry() {
    var title = $("le-title").value.trim();
    if (!title) {
      $("le-error").textContent = "Every entry needs a title.";
      return;
    }
    var tags = $("le-tags").value.split(",").map(function (t) { return t.trim(); }).filter(Boolean);
    var fields = {
      title: title,
      citation: $("le-citation").value.trim(),
      source_type: $("le-source-type").value,
      relationship: $("le-relationship").value,
      relevance_note: $("le-relevance").value,
      tags: tags,
      source_date_text: $("le-date").value.trim(),
      provenance_note: $("le-provenance").value.trim(),
      verification_state: $("le-verification").value
    };
    if (libraryEditingId) {
      var entry = doc.references.find(function (r) { return r.reference_id === libraryEditingId; });
      Object.assign(entry, fields);
    } else {
      fields.reference_id = "ref-" + randomHex32();
      fields.added_at = new Date().toISOString();
      doc.references.push(fields);
    }
    closeLibraryEditor();
    renderLibrary();
    renderSidebar();
    refreshNodeReferenceOptions();
    scheduleSave();
  }

  function verificationChipClass(state) {
    if (state === "VERIFIED") { return "chip verified"; }
    if (state === "REVIEWED") { return "chip reviewed"; }
    return "chip lead";
  }

  function renderLibrary() {
    var list = $("lib-list");
    var query = $("lib-filter").value.trim().toLowerCase();
    list.innerHTML = "";
    var entries = doc.references.filter(function (r) {
      if (!query) { return true; }
      var haystack = (r.title + " " + r.citation + " " + r.relevance_note + " " + r.tags.join(" ")).toLowerCase();
      return haystack.indexOf(query) !== -1;
    });
    if (!doc.references.length) {
      list.innerHTML = '<div class="empty-note">The library is empty. Add what you already know about — your own materials count — and let prospecting sessions grow it from there.</div>';
      return;
    }
    if (!entries.length) {
      list.innerHTML = '<div class="empty-note">Nothing matches that filter.</div>';
      return;
    }
    entries.forEach(function (entry) {
      var row = document.createElement("div");
      row.className = "row-item";
      var citationHtml = "";
      if (entry.citation) {
        if (/^https?:\/\//i.test(entry.citation)) {
          citationHtml = '<a class="mono" href="' + escapeHtml(entry.citation) + '" target="_blank" rel="noopener">' +
            escapeHtml(entry.citation) + "</a>";
        } else {
          citationHtml = '<span class="mono">' + escapeHtml(entry.citation) + "</span>";
        }
      }
      row.innerHTML =
        '<div class="ri-head">' +
          '<span class="ri-title">' + escapeHtml(entry.title) + "</span>" +
          '<span class="' + verificationChipClass(entry.verification_state) + '">' +
            VERIFICATION_LABELS[entry.verification_state] + "</span>" +
          '<span class="chip rel">' + RELATIONSHIP_LABELS[entry.relationship] + "</span>" +
        "</div>" +
        (citationHtml ? '<div style="margin-top:4px;">' + citationHtml + "</div>" : "") +
        (entry.relevance_note ? '<p class="ri-note">' + escapeHtml(entry.relevance_note) + "</p>" : "") +
        '<div class="ri-meta">' +
          '<span class="chip tag">' + SOURCE_TYPE_LABELS[entry.source_type] + "</span>" +
          entry.tags.map(function (t) { return '<span class="chip tag">' + escapeHtml(t) + "</span>"; }).join("") +
          (entry.source_date_text ? '<span class="mono">source: ' + escapeHtml(entry.source_date_text) + "</span>" : "") +
          '<span class="mono">added ' + escapeHtml(String(entry.added_at).slice(0, 10)) + "</span>" +
          (entry.provenance_note ? "<span>" + escapeHtml(entry.provenance_note) + "</span>" : "") +
          '<span class="spacer" style="flex:1;"></span>' +
          '<button class="btn tiny" data-role="edit">Edit</button>' +
          '<button class="btn tiny" data-role="remove">Remove</button>' +
        "</div>";
      row.querySelector('[data-role="edit"]').addEventListener("click", function () {
        openLibraryEditor(entry.reference_id);
      });
      row.querySelector('[data-role="remove"]').addEventListener("click", function () {
        if (!window.confirm('Remove "' + entry.title + '" from the library?')) { return; }
        doc.references = doc.references.filter(function (r) { return r.reference_id !== entry.reference_id; });
        doc.map_nodes.forEach(function (node) {
          if (node.linked_reference_id === entry.reference_id) { node.linked_reference_id = ""; }
        });
        renderLibrary();
        renderSidebar();
        refreshNodeReferenceOptions();
        scheduleSave();
      });
      list.appendChild(row);
    });
  }

  /* ---------- decision ledger ---------- */

  function initLedgerPane() {
    $("de-save").addEventListener("click", function () {
      var title = $("de-title").value.trim();
      if (!title) {
        $("de-error").textContent = "State the decision first.";
        return;
      }
      $("de-error").textContent = "";
      doc.decisions.push({
        decision_id: "dec-" + randomHex32(),
        kind: $("de-kind").value,
        title: title,
        rationale: $("de-rationale").value,
        recorded_at: new Date().toISOString()
      });
      $("de-title").value = "";
      $("de-rationale").value = "";
      renderLedger();
      renderSidebar();
      scheduleSave();
    });
  }

  function renderLedger() {
    var list = $("ledger-list");
    list.innerHTML = "";
    if (!doc.decisions.length) {
      list.innerHTML = '<div class="empty-note">No decisions recorded yet. When you choose a direction, defer something, or accept or reject a suggestion — write it down here while the why is fresh.</div>';
      return;
    }
    var ordered = doc.decisions.slice().sort(function (a, b) {
      return String(b.recorded_at).localeCompare(String(a.recorded_at));
    });
    ordered.forEach(function (decision) {
      var row = document.createElement("div");
      row.className = "row-item";
      row.innerHTML =
        '<div class="ri-head">' +
          '<span class="ri-title">' + escapeHtml(decision.title) + "</span>" +
          '<span class="chip rel">' + DECISION_KIND_LABELS[decision.kind] + "</span>" +
          '<span class="mono" style="color:var(--ink-soft);">' + escapeHtml(String(decision.recorded_at).slice(0, 10)) + "</span>" +
        "</div>" +
        (decision.rationale ? '<p class="ri-note">' + escapeHtml(decision.rationale) + "</p>" : "") +
        '<div class="ri-meta">' +
          '<span class="spacer" style="flex:1;"></span>' +
          '<button class="btn tiny" data-role="remove">Remove</button>' +
        "</div>";
      row.querySelector('[data-role="remove"]').addEventListener("click", function () {
        if (!window.confirm("Remove this decision from the ledger?")) { return; }
        doc.decisions = doc.decisions.filter(function (d) { return d.decision_id !== decision.decision_id; });
        renderLedger();
        renderSidebar();
        scheduleSave();
      });
      list.appendChild(row);
    });
  }

  /* ---------- scorecard ---------- */

  function initScorecardPane() {
    document.querySelectorAll(".lens").forEach(function (card) {
      var lensKey = card.dataset.lens;
      card.querySelectorAll("textarea[data-bind]").forEach(function (area) {
        var field = area.dataset.bind;
        area.addEventListener("input", function () {
          doc.scorecard[lensKey][field] = area.value;
          scheduleSave();
        });
      });
      var picker = card.querySelector(".level-picker");
      picker.addEventListener("click", function (event) {
        var button = event.target.closest("button[data-level]");
        if (!button) { return; }
        doc.scorecard[lensKey].level = button.dataset.level;
        renderScorecard();
        scheduleSave();
      });
    });
    renderScorecard();
  }

  function renderScorecard() {
    document.querySelectorAll(".lens").forEach(function (card) {
      var lensKey = card.dataset.lens;
      var lens = doc.scorecard[lensKey];
      card.querySelectorAll("textarea[data-bind]").forEach(function (area) {
        area.value = lens[area.dataset.bind];
      });
      card.querySelectorAll(".level-picker button").forEach(function (button) {
        button.classList.toggle("active", button.dataset.level === lens.level);
      });
    });
  }

  /* ---------- invention map ---------- */

  var NODE_WIDTH = 156;
  var NODE_HEIGHT = 52;
  var selectedNodeId = null;
  var selectedEdgeId = null;
  var connectSourceId = null;
  var isConnectMode = false;

  function nodeById(nodeId) {
    return doc.map_nodes.find(function (n) { return n.node_id === nodeId; }) || null;
  }

  function setMapStatus(text) { $("map-status").textContent = text; }

  function initMapPane() {
    $("map-add").addEventListener("click", function () {
      var frame = $("map-frame");
      var node = {
        node_id: "node-" + randomHex32(),
        kind: $("map-kind").value,
        label: NODE_KIND_LABELS[$("map-kind").value],
        note: "",
        x: frame.scrollLeft + 80 + (doc.map_nodes.length % 5) * 30,
        y: frame.scrollTop + 60 + (doc.map_nodes.length % 7) * 26,
        linked_reference_id: ""
      };
      doc.map_nodes.push(node);
      selectNode(node.node_id);
      renderMap();
      renderSidebar();
      scheduleSave();
    });

    $("map-connect").addEventListener("click", function () {
      isConnectMode = !isConnectMode;
      connectSourceId = null;
      $("map-connect").classList.toggle("primary", isConnectMode);
      setMapStatus(isConnectMode ? "Click the first element…" : "");
    });

    $("map-delete").addEventListener("click", deleteMapSelection);

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") { return; }
      if (isConnectMode) {
        isConnectMode = false;
        connectSourceId = null;
        $("map-connect").classList.remove("primary");
        setMapStatus("");
      }
    });

    $("ne-label").addEventListener("input", function (e) {
      var node = nodeById(selectedNodeId);
      if (!node) { return; }
      node.label = e.target.value;
      renderMap();
      scheduleSave();
    });
    $("ne-kind").addEventListener("change", function (e) {
      var node = nodeById(selectedNodeId);
      if (!node) { return; }
      node.kind = e.target.value;
      renderMap();
      scheduleSave();
    });
    $("ne-note").addEventListener("input", function (e) {
      var node = nodeById(selectedNodeId);
      if (!node) { return; }
      node.note = e.target.value;
      scheduleSave();
    });
    $("ne-reference").addEventListener("change", function (e) {
      var node = nodeById(selectedNodeId);
      if (!node) { return; }
      node.linked_reference_id = e.target.value;
      scheduleSave();
    });
    $("ee-label").addEventListener("input", function (e) {
      var edge = doc.map_edges.find(function (x) { return x.edge_id === selectedEdgeId; });
      if (!edge) { return; }
      edge.label = e.target.value;
      renderMap();
      scheduleSave();
    });

    refreshNodeReferenceOptions();
    initMapPointerHandling();
  }

  function refreshNodeReferenceOptions() {
    var select = $("ne-reference");
    var current = select.value;
    select.innerHTML = '<option value="">— none —</option>' +
      doc.references.map(function (r) {
        return '<option value="' + escapeHtml(r.reference_id) + '">' + escapeHtml(r.title) + "</option>";
      }).join("");
    select.value = current;
  }

  function deleteMapSelection() {
    if (selectedNodeId) {
      var removedNodeId = selectedNodeId;
      doc.map_nodes = doc.map_nodes.filter(function (n) { return n.node_id !== removedNodeId; });
      doc.map_edges = doc.map_edges.filter(function (e) {
        return e.source_node_id !== removedNodeId && e.target_node_id !== removedNodeId;
      });
      selectNode(null);
    } else if (selectedEdgeId) {
      var removedEdgeId = selectedEdgeId;
      doc.map_edges = doc.map_edges.filter(function (e) { return e.edge_id !== removedEdgeId; });
      selectEdge(null);
    }
    renderMap();
    renderSidebar();
    scheduleSave();
  }

  function selectNode(nodeId) {
    selectedNodeId = nodeId;
    selectedEdgeId = null;
    var node = nodeById(nodeId);
    $("node-editor").hidden = !node;
    $("edge-editor").hidden = true;
    $("map-delete").disabled = !node;
    if (node) {
      $("node-editor-title").textContent = "Element — " + (NODE_KIND_LABELS[node.kind] || node.kind);
      $("ne-label").value = node.label;
      $("ne-kind").value = node.kind;
      $("ne-note").value = node.note;
      refreshNodeReferenceOptions();
      $("ne-reference").value = node.linked_reference_id || "";
    }
  }

  function selectEdge(edgeId) {
    selectedEdgeId = edgeId;
    selectedNodeId = null;
    var edge = doc.map_edges.find(function (e) { return e.edge_id === edgeId; }) || null;
    $("edge-editor").hidden = !edge;
    $("node-editor").hidden = true;
    $("map-delete").disabled = !edge;
    if (edge) { $("ee-label").value = edge.label; }
  }

  function handleNodeClick(nodeId) {
    if (!isConnectMode) {
      selectNode(nodeId);
      renderMap();
      return;
    }
    if (!connectSourceId) {
      connectSourceId = nodeId;
      setMapStatus("Now click the element it connects to.");
      return;
    }
    if (connectSourceId !== nodeId) {
      doc.map_edges.push({
        edge_id: "edge-" + randomHex32(),
        source_node_id: connectSourceId,
        target_node_id: nodeId,
        label: ""
      });
      scheduleSave();
    }
    connectSourceId = null;
    isConnectMode = false;
    $("map-connect").classList.remove("primary");
    setMapStatus("");
    renderMap();
  }

  var dragState = null;

  function initMapPointerHandling() {
    var svg = $("map-svg");

    svg.addEventListener("pointerdown", function (event) {
      var nodeGroup = event.target.closest(".map-node");
      if (!nodeGroup) { return; }
      var node = nodeById(nodeGroup.dataset.nodeId);
      if (!node) { return; }
      var point = svgPoint(svg, event);
      dragState = {
        nodeId: node.node_id,
        offsetX: point.x - node.x,
        offsetY: point.y - node.y,
        moved: false
      };
      svg.setPointerCapture(event.pointerId);
    });

    svg.addEventListener("pointermove", function (event) {
      if (!dragState) { return; }
      var node = nodeById(dragState.nodeId);
      if (!node) { return; }
      var point = svgPoint(svg, event);
      var newX = Math.max(0, Math.min(1600 - NODE_WIDTH, point.x - dragState.offsetX));
      var newY = Math.max(0, Math.min(1200 - NODE_HEIGHT, point.y - dragState.offsetY));
      if (Math.abs(newX - node.x) > 2 || Math.abs(newY - node.y) > 2) { dragState.moved = true; }
      node.x = newX;
      node.y = newY;
      renderMap();
    });

    svg.addEventListener("pointerup", function (event) {
      if (!dragState) { return; }
      var wasDrag = dragState.moved;
      var nodeId = dragState.nodeId;
      dragState = null;
      if (wasDrag) {
        scheduleSave();
      } else {
        handleNodeClick(nodeId);
      }
    });

    svg.addEventListener("click", function (event) {
      var edgeGroup = event.target.closest(".map-edge");
      if (edgeGroup) {
        selectEdge(edgeGroup.dataset.edgeId);
        renderMap();
        return;
      }
      if (!event.target.closest(".map-node")) {
        selectNode(null);
        selectEdge(null);
        renderMap();
      }
    });
  }

  function svgPoint(svg, event) {
    var rect = svg.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
  }

  function truncateLabel(text, maxChars) {
    if (text.length <= maxChars) { return text; }
    return text.slice(0, maxChars - 1) + "…";
  }

  function renderMap() {
    var edgesGroup = $("map-edges");
    var nodesGroup = $("map-nodes");
    var svgNS = "http://www.w3.org/2000/svg";
    edgesGroup.innerHTML = "";
    nodesGroup.innerHTML = "";

    doc.map_edges.forEach(function (edge) {
      var source = nodeById(edge.source_node_id);
      var target = nodeById(edge.target_node_id);
      if (!source || !target) { return; }
      var group = document.createElementNS(svgNS, "g");
      group.setAttribute("class", "map-edge" + (edge.edge_id === selectedEdgeId ? " selected" : ""));
      group.dataset.edgeId = edge.edge_id;
      var x1 = source.x + NODE_WIDTH / 2;
      var y1 = source.y + NODE_HEIGHT / 2;
      var x2 = target.x + NODE_WIDTH / 2;
      var y2 = target.y + NODE_HEIGHT / 2;
      var line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", x1);
      line.setAttribute("y1", y1);
      line.setAttribute("x2", x2);
      line.setAttribute("y2", y2);
      group.appendChild(line);
      var hit = document.createElementNS(svgNS, "line");
      hit.setAttribute("x1", x1);
      hit.setAttribute("y1", y1);
      hit.setAttribute("x2", x2);
      hit.setAttribute("y2", y2);
      hit.setAttribute("stroke", "transparent");
      hit.setAttribute("stroke-width", "12");
      group.appendChild(hit);
      if (edge.label) {
        var text = document.createElementNS(svgNS, "text");
        text.setAttribute("x", (x1 + x2) / 2);
        text.setAttribute("y", (y1 + y2) / 2 - 5);
        text.setAttribute("text-anchor", "middle");
        text.textContent = edge.label;
        group.appendChild(text);
      }
      edgesGroup.appendChild(group);
    });

    doc.map_nodes.forEach(function (node) {
      var group = document.createElementNS(svgNS, "g");
      group.setAttribute(
        "class",
        "map-node kind-" + node.kind +
          (node.node_id === selectedNodeId ? " selected" : "") +
          (node.node_id === connectSourceId ? " selected" : "")
      );
      group.dataset.nodeId = node.node_id;
      group.setAttribute("transform", "translate(" + node.x + "," + node.y + ")");
      group.style.cursor = "grab";
      var rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("width", NODE_WIDTH);
      rect.setAttribute("height", NODE_HEIGHT);
      group.appendChild(rect);
      var kindText = document.createElementNS(svgNS, "text");
      kindText.setAttribute("x", 10);
      kindText.setAttribute("y", 16);
      kindText.setAttribute("class", "node-kind");
      kindText.textContent = (NODE_KIND_LABELS[node.kind] || node.kind).toUpperCase() +
        (node.linked_reference_id ? " · REF" : "");
      group.appendChild(kindText);
      var labelText = document.createElementNS(svgNS, "text");
      labelText.setAttribute("x", 10);
      labelText.setAttribute("y", 36);
      labelText.textContent = truncateLabel(node.label || "(unnamed)", 22);
      group.appendChild(labelText);
      nodesGroup.appendChild(group);
    });
  }

  /* ---------- export pane ---------- */

  function initExportPane() {
    $("export-link").href = "matter/" + MATTER_ID + "/export.zip";
    $("raw-link").href = "matter/" + MATTER_ID + "/raw";
    $("delete-matter").addEventListener("click", function () {
      var confirmed = window.confirm(
        'Delete "' + doc.title + '" from this machine?\n\nThis cannot be undone. If in doubt, download the export first.'
      );
      if (!confirmed) { return; }
      fetch(API_URL, { method: "DELETE" }).then(function (response) {
        if (!response.ok) { throw new Error("delete failed"); }
        window.location.href = "./";
      }).catch(function () {
        window.alert("The matter couldn't be deleted. Try again.");
      });
    });
  }

  /* ---------- boot ---------- */

  fetch(API_URL).then(function (response) {
    if (!response.ok) { throw new Error("load failed (" + response.status + ")"); }
    return response.json();
  }).then(function (loaded) {
    doc = loaded;
    applyTheme();
    renderSidebar();
    initNav();
    initHomePane();
    initBriefPane();
    renderHarvest();
    initLibraryPane();
    renderLibrary();
    initLedgerPane();
    renderLedger();
    initScorecardPane();
    initMapPane();
    renderMap();
    initExportPane();
    renderContinue();
    $("load-remote-update").addEventListener("click", function () {
      if (!pendingRemoteDoc || isSaving) { return; }
      if (saveTimer) { clearTimeout(saveTimer); saveTimer = null; }
      applyRemoteDocument(pendingRemoteDoc);
    });
    startPolling();
    setSaveStatus("Loaded " + new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  }).catch(function () {
    setSaveStatus("Couldn't load this matter — reload the page.", true);
  });
})();
