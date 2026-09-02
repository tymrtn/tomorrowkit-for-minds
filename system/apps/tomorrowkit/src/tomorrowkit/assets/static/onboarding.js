/* Tomorrowkit orientation.
   Five bounded choices become the initial matter context. Detailed invention
   harvesting belongs in the Mind conversation, one question at a time. */

(function () {
  "use strict";

  var QUESTIONS = [
    {
      key: "idea_state",
      kicker: "The invention",
      title: "How far has the idea moved out of your head?",
      help: "Choose the closest answer. Tomorrowkit will ask about the details later.",
      options: [
        { value: "IN_MY_HEAD", label: "Mostly in my head", note: "I can explain the direction, but the mechanism is still taking shape." },
        { value: "WRITTEN_OR_BUILT", label: "Written down or built", note: "I have notes, sketches, a prototype, code, tests, or another concrete record." },
        { value: "DRAFT_PROVISIONAL", label: "I have a draft provisional", note: "A draft exists, but I want to test its coverage before relying on it." },
        { value: "FILED", label: "A provisional has already been filed", note: "I need to organize what was filed and what has changed since." }
      ]
    },
    {
      key: "disclosure_state",
      kicker: "Timing",
      title: "Who outside your immediate work has seen it?",
      help: "This helps Tomorrowkit decide which dates and disclosures to clarify first.",
      options: [
        { value: "PRIVATE", label: "No one outside my private work", note: "I have not shown, sold, published, or offered it publicly." },
        { value: "CONFIDENTIAL_ONLY", label: "Only people under confidentiality", note: "I have shared it, but only in a confidential setting." },
        { value: "MAYBE_PUBLIC", label: "I am not sure what counts", note: "There may have been a pitch, demo, repository, paper, or conversation to review." },
        { value: "PUBLIC_OR_COMMERCIAL", label: "It has been public or commercial", note: "It has been shown, sold, offered, published, or otherwise disclosed." }
      ]
    },
    {
      key: "objectives",
      kicker: "Purpose",
      title: "What do you want this work to support?",
      help: "Choose up to three. These choices shape what Tomorrowkit asks you to define and preserve.",
      multiple: true,
      max: 3,
      options: [
        { value: "PROTECT_PRODUCT", label: "Protect a product or service", note: "Keep competitors from copying the part customers care about." },
        { value: "LICENSE_OR_PARTNER", label: "License or find a partner", note: "Build a record another company can evaluate." },
        { value: "ENCIRCLE_OR_BLOCK", label: "Block design-arounds", note: "Map variations around the core mechanism." },
        { value: "FUNDRAISE_OR_ACQUIRE", label: "Support fundraising or acquisition", note: "Make the technical asset easier to inspect." },
        { value: "BANK_OPTIONALITY", label: "Preserve options", note: "Capture the invention now while the business path is still open." },
        { value: "PUBLISH_OR_PUBLIC_BENEFIT", label: "Publish for public benefit", note: "Understand what should be preserved before publication." },
        { value: "UNDERSTAND_OPTIONS", label: "Understand my options", note: "Get oriented before choosing a filing or business path." }
      ]
    },
    {
      key: "materials_state",
      kicker: "Source material",
      title: "What can Tomorrowkit work from today?",
      help: "You will decide what to share. This only sets the starting posture.",
      options: [
        { value: "CONVERSATION_ONLY", label: "A conversation", note: "The useful detail is still in my head." },
        { value: "NOTES_OR_SKETCHES", label: "Notes or sketches", note: "I have informal descriptions, diagrams, logs, or screenshots." },
        { value: "TECHNICAL_MATERIALS", label: "Technical materials", note: "I have code, test results, specifications, models, or prototypes." },
        { value: "DRAFT_OR_FILING", label: "A draft or filing", note: "There is already patent-oriented material to inspect." }
      ]
    },
    {
      key: "collaboration_style",
      kicker: "Working style",
      title: "How should Tomorrowkit work with you?",
      help: "Consequential facts and decisions still come back to you for review.",
      options: [
        { value: "INTERVIEW_ME", label: "Interview me", note: "Ask one focused question at a time and build the record from my answers." },
        { value: "GUIDED_CHOICES", label: "Give me guided choices", note: "Offer concrete paths when a blank page would slow me down." },
        { value: "BACKGROUND_WITH_GATES", label: "Work in the background, then check in", note: "Organize and research between clear approval points." },
        { value: "HIGH_AUTONOMY", label: "Move quickly with high autonomy", note: "Develop the record actively, while keeping assumptions and approvals visible." }
      ]
    }
  ];

  var INSIGHTS = {
    idea_state: {
      IN_MY_HEAD: "A provisional cannot protect a theme by itself. It can support only the technical territory you can actually describe, so Tomorrowkit will help turn the direction into a concrete mechanism.",
      WRITTEN_OR_BUILT: "Notes, sketches, code, and prototypes are more than background. They anchor what existed before the agent starts proposing alternatives.",
      DRAFT_PROVISIONAL: "A draft is not strong because it sounds patent-like. The useful question is which technical terrain it actually teaches and which later claims it could support.",
      FILED: "A filing fixes a date for what it adequately describes. Improvements added later may carry a later date, so Tomorrowkit keeps filed and later material visibly separate."
    },
    disclosure_state: {
      PRIVATE: "No outside disclosure is identified yet. Tomorrowkit will still keep upcoming demos, pitches, publications, offers, and filings visible because timing can change the available strategy.",
      CONFIDENTIAL_ONLY: "Confidential sharing is different from public disclosure, but the record should still preserve who received what, when, and under which understanding.",
      MAYBE_PUBLIC: "You do not need to decide the legal effect now. Tomorrowkit will reconstruct what was shared, with whom, and when, without turning uncertainty into a verdict.",
      PUBLIC_OR_COMMERCIAL: "The exact material and date matter more than a generic warning. Source Lock will reconstruct the event calmly before the invention is expanded."
    },
    objectives: "Patentability is a constraint, not the objective. Your chosen outcome determines which technical control points, design-arounds, evidence, and future options are worth preserving.",
    materials_state: {
      CONVERSATION_ONLY: "The first job is invention capture: preserve your language and decisions before model-generated possibilities enter the record.",
      NOTES_OR_SKETCHES: "Tomorrowkit will label and preserve these as inventor source before using AI to expand the design space.",
      TECHNICAL_MATERIALS: "Working evidence can reveal mechanisms, limits, failure cases, and alternatives that a polished summary often hides.",
      DRAFT_OR_FILING: "Patent-oriented material is still evidence, not truth. Tomorrowkit will compare what it says with the invention, the dates, and the terrain you actually care about."
    },
    collaboration_style: {
      INTERVIEW_ME: "Tomorrowkit will ask one focused question, update the record, and let your answer determine the next question.",
      GUIDED_CHOICES: "Tomorrowkit can propose concrete alternatives, but it will keep proposals distinct until you understand, change, accept, or reject them.",
      BACKGROUND_WITH_GATES: "The agent can organize and investigate between decisions while stopping for source facts, objectives, terrain, disclosure posture, and other human-only calls.",
      HIGH_AUTONOMY: "High autonomy changes how much background work happens between check-ins. It does not transfer inventorship, approval, filing, publication, or spending decisions to the agent."
    }
  };

  var answers = { objectives: [] };
  var currentIndex = 0;
  var isCreating = false;

  function $(id) { return document.getElementById(id); }

  function escapeHtml(text) {
    return String(text == null ? "" : text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function selectedValues(question) {
    if (question.multiple) { return answers[question.key] || []; }
    return answers[question.key] ? [answers[question.key]] : [];
  }

  function renderQuestion(focusValue) {
    var question = QUESTIONS[currentIndex];
    var selected = selectedValues(question);
    var selectionHelp = question.multiple ? '<p class="quiz-limit">Select up to ' + question.max + '.</p>' : "";
    var insight = insightFor(question, selected);
    var insightHtml = insight ?
      '<aside class="quiz-insight"><span>Why this matters</span><p>' + escapeHtml(insight) + '</p></aside>' : "";
    $("quiz-question").innerHTML =
      '<p class="eyebrow">' + escapeHtml(question.kicker) + "</p>" +
      '<h2 id="question-title">' + escapeHtml(question.title) + "</h2>" +
      '<p class="question-help">' + escapeHtml(question.help) + "</p>" +
      selectionHelp +
      '<div class="choice-list" role="group" aria-labelledby="question-title">' +
        question.options.map(function (option) {
          var isSelected = selected.indexOf(option.value) !== -1;
          return '<button type="button" class="choice-card' + (isSelected ? " selected" : "") + '" ' +
            'data-value="' + option.value + '" aria-pressed="' + String(isSelected) + '">' +
              '<span class="choice-control" aria-hidden="true"></span>' +
              '<span><strong>' + escapeHtml(option.label) + '</strong><small>' + escapeHtml(option.note) + "</small></span>" +
            "</button>";
        }).join("") +
      "</div>" + insightHtml;

    $("quiz-progress-copy").textContent = "Question " + (currentIndex + 1) + " of " + QUESTIONS.length;
    $("quiz-progress-bar").style.width = (((currentIndex + 1) / QUESTIONS.length) * 100) + "%";
    $("quiz-back").hidden = currentIndex === 0;
    $("quiz-next").disabled = selected.length === 0;
    $("quiz-next").textContent = currentIndex === QUESTIONS.length - 1 ? "See my starting point" : "Continue";
    updateSelectionNote(question, selected.length);
    $("quiz-error").textContent = "";

    $("quiz-question").querySelector(".choice-list").addEventListener("click", function (event) {
      var button = event.target.closest("button[data-value]");
      if (!button) { return; }
      chooseOption(question, button.dataset.value);
    });
    if (focusValue) {
      var focusButton = Array.prototype.find.call(
        $("quiz-question").querySelectorAll("button[data-value]"),
        function (button) { return button.dataset.value === focusValue; }
      );
      if (focusButton) { focusButton.focus(); return; }
    }
    $("quiz-question").focus();
  }

  function insightFor(question, selected) {
    if (!selected.length) { return ""; }
    var insight = INSIGHTS[question.key];
    if (typeof insight === "string") { return insight; }
    return insight && insight[selected[0]] ? insight[selected[0]] : "";
  }

  function chooseOption(question, value) {
    if (question.multiple) {
      var current = (answers[question.key] || []).slice();
      var existingIndex = current.indexOf(value);
      if (existingIndex !== -1) {
        current.splice(existingIndex, 1);
      } else if (current.length < question.max) {
        current.push(value);
      } else {
        $("quiz-error").textContent = "Choose up to three priorities. Remove one before adding another.";
        return;
      }
      answers[question.key] = current;
    } else {
      answers[question.key] = value;
    }
    renderQuestion(value);
  }

  function updateSelectionNote(question, count) {
    if (!question.multiple) {
      $("quiz-selection-note").textContent = "";
      return;
    }
    $("quiz-selection-note").textContent = count ? count + " of " + question.max + " selected" : "Choose at least one";
  }

  function optionFor(questionKey, value) {
    var question = QUESTIONS.find(function (item) { return item.key === questionKey; });
    return question.options.find(function (option) { return option.value === value; });
  }

  function resultHeadline() {
    var headlines = {
      IN_MY_HEAD: "First, capture the mechanism before it drifts.",
      WRITTEN_OR_BUILT: "Start by locking the facts already in your materials.",
      DRAFT_PROVISIONAL: "Start by testing what the draft supports.",
      FILED: "Start by separating what was filed from what came later."
    };
    return headlines[answers.idea_state];
  }

  function timingResult() {
    var copy = {
      PRIVATE: "No outside disclosure is currently identified. Tomorrowkit will still confirm relevant dates.",
      CONFIDENTIAL_ONLY: "The first review will record who received the material and under what confidentiality terms.",
      MAYBE_PUBLIC: "The first review will identify possible demos, pitches, repositories, papers, offers, or sales and their dates.",
      PUBLIC_OR_COMMERCIAL: "Dates and exactly what was disclosed come first because they may affect available options."
    };
    return copy[answers.disclosure_state];
  }

  function renderResult() {
    var style = optionFor("collaboration_style", answers.collaboration_style);
    var materials = optionFor("materials_state", answers.materials_state);
    var objectiveLabels = answers.objectives.map(function (value) {
      return optionFor("objectives", value).label;
    });

    $("result-title").textContent = resultHeadline();
    $("result-summary").textContent = timingResult();
    $("result-grid").innerHTML =
      '<article><span class="result-label">What you want to support</span><strong>' +
        escapeHtml(objectiveLabels.join(", ")) +
      '</strong></article>' +
      '<article><span class="result-label">What exists today</span><strong>' +
        escapeHtml(materials.label) +
      '</strong><p>' + escapeHtml(materials.note) + '</p></article>' +
      '<article><span class="result-label">How Tomorrowkit should work</span><strong>' +
        escapeHtml(style.label) +
      '</strong><p>' + escapeHtml(style.note) + "</p></article>";
    $("orientation-quiz").hidden = true;
    $("orientation-result").hidden = false;
    $("orientation-result").focus();
  }

  function createWorkspace() {
    if (isCreating) { return; }
    isCreating = true;
    $("create-error").textContent = "";
    $("create-workspace").disabled = true;
    $("create-workspace").textContent = "Creating workspace…";
    fetch("api/orientation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        idea_state: answers.idea_state,
        disclosure_state: answers.disclosure_state,
        objectives: answers.objectives,
        materials_state: answers.materials_state,
        collaboration_style: answers.collaboration_style
      })
    }).then(function (response) {
      if (!response.ok) { throw new Error("create failed (" + response.status + ")"); }
      return response.json();
    }).then(function (matter) {
      window.location.href = "matter/" + matter.matter_id;
    }).catch(function () {
      isCreating = false;
      $("create-workspace").disabled = false;
      $("create-workspace").textContent = "Create my workspace";
      $("create-error").textContent = "The workspace could not be created. Your choices are still here; try again.";
    });
  }

  $("quiz-next").addEventListener("click", function () {
    if (!selectedValues(QUESTIONS[currentIndex]).length) { return; }
    if (currentIndex === QUESTIONS.length - 1) {
      renderResult();
      return;
    }
    currentIndex += 1;
    renderQuestion();
  });

  $("quiz-back").addEventListener("click", function () {
    if (currentIndex === 0) { return; }
    currentIndex -= 1;
    renderQuestion();
  });

  $("result-back").addEventListener("click", function () {
    $("orientation-result").hidden = true;
    $("orientation-quiz").hidden = false;
    currentIndex = QUESTIONS.length - 1;
    renderQuestion();
  });

  $("create-workspace").addEventListener("click", createWorkspace);
  renderQuestion();
})();
