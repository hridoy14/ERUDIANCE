// ---- Access role (placeholder until real auth/roles exist) ----
// Everything gated by CURRENT_ROLE lives behind the 'role-<name>' class on
// <body>. When real roles/auth are wired up later, only this one line needs
// to change (or be set dynamically) - nothing else in this file should need
// to know how the role was determined.
var CURRENT_ROLE = 'content-editor';
document.body.classList.add('role-' + CURRENT_ROLE);

// ---- Per-document storage scope ----
// Offer Letter, Invoice and Employee Invoice all load this same app.js and
// share element classes (.content, .footer, .brand-details, etc.), so every
// localStorage key below must be scoped by page - otherwise saving on one
// document (content edits, design colors, signature) would silently leak
// into / overwrite the others on next load.
var PAGE_ID = (location.pathname.split('/').pop() || 'erudience_offer_letter.html').replace(/\.html$/, '');

// ---- Print / PDF filename logic ----
  var _originalDocumentTitle = document.title;

  // Fallback filename per document, used whenever the page has nothing more
  // specific typed in yet (or isn't one of the documents with a dedicated
  // naming rule below).
  var PAGE_DEFAULT_FILENAME = {
    'erudience_offer_letter': 'Erudience-Offer-Letter',
    'invoice': 'Erudience-Invoice',
    'employee-invoice': 'Erudience-Employee-Invoice',
    'agreement-letter': 'Erudience-Agreement-Letter',
    'client-proposal': 'Erudience-Client-Proposal'
  };

  function printOfferLetter(){
    var defaultName = PAGE_DEFAULT_FILENAME[PAGE_ID] || 'Erudience-Document';
    var filename = '';

    var nameEl = document.querySelector('.to-block b[contenteditable]');
    var titleEl = document.querySelector('.details-box .value[contenteditable]');
    var invNumEl = document.querySelector('.doctitle span[contenteditable]');

    if(nameEl || titleEl){
      // Offer Letter: "Candidate Name Job Title"
      var name = nameEl ? nameEl.textContent.trim() : '';
      var jobTitle = titleEl ? titleEl.textContent.trim() : '';
      if(name === (nameEl && nameEl.getAttribute('data-placeholder'))) name = '';
      if(jobTitle === (titleEl && titleEl.getAttribute('data-placeholder'))) jobTitle = '';
      filename = [name, jobTitle].filter(Boolean).join(' ').trim();
    } else if(invNumEl){
      // Invoice: "Invoice #INV-0142"
      var num = invNumEl.textContent.trim();
      if(num === invNumEl.getAttribute('data-placeholder')) num = '';
      filename = num ? ('Invoice ' + num) : '';
    }

    if(!filename) filename = defaultName;

    filename = filename.replace(/[^A-Za-z0-9 _-]/g, '');
    filename = filename.replace(/\s+/g, '-');
    filename = filename.substring(0, 80);
    if(!filename) filename = defaultName;

    document.title = filename;
    window.print();
  }

  window.addEventListener('afterprint', function(){
    document.title = _originalDocumentTitle;
  });

// ---- Signature Style panel ----
(function(){
  var STORAGE_KEY = 'erudienceSignatureSettings_' + PAGE_ID;

  var closingBlock = document.getElementById('closingBlock');
  var sigArea = document.getElementById('sigArea');
  var sigPrintedName = document.getElementById('sigPrintedName');
  var nameInput = document.getElementById('sigNameInput');
  var fontSelect = document.getElementById('sigFontSelect');
  var sizeInput = document.getElementById('sigSizeInput');
  var sizeValue = document.getElementById('sigSizeValue');
  var alignSelect = document.getElementById('sigAlignSelect');
  var boldToggle = document.getElementById('sigBoldToggle');
  var italicToggle = document.getElementById('sigItalicToggle');
  var underlineToggle = document.getElementById('sigUnderlineToggle');
  var colorInput = document.getElementById('sigColorInput');
  var fileInput = document.getElementById('sigFileInput');
  var modeTypeRadio = document.getElementById('sigModeType');
  var modeUploadRadio = document.getElementById('sigModeUpload');
  var typeControls = document.getElementById('sigTypeControls');
  var uploadControls = document.getElementById('sigUploadControls');

  var lastImageDataUrl = null;

  function currentMode(){
    return modeUploadRadio.checked ? 'upload' : 'type';
  }

  function applyAlign(){
    closingBlock.style.textAlign = alignSelect.value;
    var divider = document.querySelector('.signature-divider');
    if(divider){
      if(alignSelect.value === 'center'){
        divider.style.marginLeft = 'auto';
        divider.style.marginRight = 'auto';
      } else if(alignSelect.value === 'right'){
        divider.style.marginLeft = 'auto';
        divider.style.marginRight = '0';
      } else {
        divider.style.marginLeft = '0';
        divider.style.marginRight = 'auto';
      }
    }
  }

  function escapeHtml(str){
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function formatPrintedName(name){
    return name.split(' ').map(function(word){
      if(!word) return word;
      return '<span class="sig-name-cap">' + escapeHtml(word.charAt(0)) + '</span>' + escapeHtml(word.slice(1));
    }).join(' ');
  }

  function renderTypedSignature(){
    var name = nameInput.value.trim();

    // Always render the same contenteditable element, filled in or not, so
    // the empty state is directly clickable/typeable on the page too - not
    // just via the sidebar's "Type name" field. When empty, CSS shows the
    // data-placeholder text (same convention as every other field).
    sigArea.innerHTML = '<div class="signature-script" id="sigText" contenteditable="plaintext-only" data-placeholder="Type a name above to generate your signature">' +
      escapeHtml(name) +
      '</div>';
    var sigText = document.getElementById('sigText');
    sigText.style.fontFamily = fontSelect.value;
    sigText.style.setProperty('--sig-font-size', sizeInput.value + 'px');
    sigText.style.fontWeight = boldToggle.checked ? '700' : '400';
    sigText.style.fontStyle = italicToggle.checked ? 'italic' : 'normal';
    sigText.style.textDecoration = underlineToggle.checked ? 'underline' : 'none';
    sigText.style.color = colorInput.value;

    // Editing the signature directly on the page (click it, type) should stay
    // in sync with the sidebar's "Type name" field and persist the same way.
    sigText.addEventListener('input', function(){
      var liveName = sigText.textContent.trim();
      nameInput.value = liveName;
      if(sigPrintedName) sigPrintedName.innerHTML = formatPrintedName(liveName);
      save();
    });

    if(name && sigPrintedName) sigPrintedName.innerHTML = formatPrintedName(name);
  }

  function renderImageSignature(dataUrl){
    lastImageDataUrl = dataUrl;
    sigArea.innerHTML = '<img class="sig-image" src="' + dataUrl + '" alt="Signature">';
  }

  function renderEmptySignature(message){
    sigArea.innerHTML = '<div class="sig-empty">' + message + '</div>';
  }

  function setMode(mode){
    if(mode === 'upload'){
      typeControls.style.display = 'none';
      uploadControls.style.display = '';
      if(lastImageDataUrl) renderImageSignature(lastImageDataUrl);
      else renderEmptySignature('No signature uploaded yet');
    } else {
      typeControls.style.display = '';
      uploadControls.style.display = 'none';
      renderTypedSignature();
    }
  }

  function save(){
    try{
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        mode: currentMode(),
        name: nameInput.value,
        font: fontSelect.value,
        size: sizeInput.value,
        align: alignSelect.value,
        bold: boldToggle.checked,
        italic: italicToggle.checked,
        underline: underlineToggle.checked,
        color: colorInput.value,
        image: lastImageDataUrl
      }));
    }catch(e){}
  }

  modeTypeRadio.addEventListener('change', function(){ setMode('type'); save(); });
  modeUploadRadio.addEventListener('change', function(){ setMode('upload'); save(); });

  [nameInput, fontSelect, colorInput].forEach(function(el){
    el.addEventListener('input', function(){ renderTypedSignature(); save(); });
  });
  [boldToggle, italicToggle, underlineToggle].forEach(function(el){
    el.addEventListener('change', function(){ renderTypedSignature(); save(); });
  });
  alignSelect.addEventListener('input', function(){ applyAlign(); save(); });
  sizeInput.addEventListener('input', function(){
    sizeValue.textContent = sizeInput.value + 'px';
    renderTypedSignature();
    save();
  });

  fileInput.addEventListener('change', function(e){
    var file = e.target.files && e.target.files[0];
    if(!file) return;
    var reader = new FileReader();
    reader.onload = function(ev){
      renderImageSignature(ev.target.result);
      save();
    };
    reader.readAsDataURL(file);
  });

  applyAlign();

  try{
    var saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if(saved){
      nameInput.value = saved.name || '';
      if(saved.font) fontSelect.value = saved.font;
      if(saved.size){ sizeInput.value = saved.size; sizeValue.textContent = saved.size + 'px'; }
      if(saved.align) alignSelect.value = saved.align;
      boldToggle.checked = !!saved.bold;
      italicToggle.checked = !!saved.italic;
      underlineToggle.checked = !!saved.underline;
      if(saved.color) colorInput.value = saved.color;
      applyAlign();
      if(saved.mode === 'upload' && saved.image){
        modeUploadRadio.checked = true;
        setMode('upload');
      } else {
        setMode('type');
      }
    } else {
      // No saved settings for this page yet. Some documents (Invoice, Employee
      // Invoice) ship with a signature already baked into the markup - don't
      // wipe it out with the empty-state placeholder. Just pick up its name
      // into the input so the customizer controls reflect what's on the page.
      var existingSig = sigArea.querySelector('.signature-script');
      if(existingSig){
        nameInput.value = existingSig.textContent.trim();
        // Keep it directly clickable/editable on the page itself, in sync
        // with the sidebar's "Type name" field, without re-rendering it
        // (which would lose its baked-in default styling).
        if(!existingSig.hasAttribute('contenteditable')) existingSig.setAttribute('contenteditable', 'plaintext-only');
        existingSig.addEventListener('input', function(){
          var liveName = existingSig.textContent.trim();
          nameInput.value = liveName;
          if(sigPrintedName) sigPrintedName.innerHTML = formatPrintedName(liveName);
          save();
        });
      } else {
        renderTypedSignature();
      }
    }
  }catch(e){
    renderEmptySignature('Type a name above to generate your signature');
  }
})();

// ---- Secondary signature fields (e.g. Agreement Letter's Employee signature) ----
// Anything inside #closingBlock other than the CEO's #sigArea/#sigPrintedName
// is intentionally skipped by the generic content-persistence snapshot below,
// to avoid it fighting with the Signature Style panel above. Fields like the
// Employee's own signature/name still need *some* persistence though, so give
// each a tiny dedicated save/restore keyed by its own id.
(function(){
  var KEY = 'erudienceSecondarySignature_' + PAGE_ID;
  var fields = [
    document.getElementById('empSignatureText'),
    document.getElementById('empSignatureName')
  ].filter(Boolean);
  if(!fields.length) return;

  var saveTimer = null;
  function save(){
    try{
      var data = {};
      fields.forEach(function(el){ data[el.id] = el.textContent; });
      localStorage.setItem(KEY, JSON.stringify(data));
    }catch(e){}
  }
  function debounceSave(){
    clearTimeout(saveTimer);
    saveTimer = setTimeout(save, 400);
  }

  try{
    var saved = JSON.parse(localStorage.getItem(KEY));
    if(saved){
      fields.forEach(function(el){
        if(saved[el.id] != null) el.textContent = saved[el.id];
      });
    }
  }catch(e){}

  fields.forEach(function(el){
    el.addEventListener('input', debounceSave);
  });
})();

// ---- Custom Edit: toggle, format bar, logo replace ----
(function(){
  var toggleBtn = document.getElementById('customEditToggle');
  var toggleLabel = document.getElementById('customEditToggleLabel');
  var editHint = document.getElementById('editModeHint');
  var formatBar = document.getElementById('editFormatBar');
  var logoImg = document.getElementById('brandLogoImg');
  var logoFileInput = document.getElementById('logoFileInput');

  var EDITABLE_REGIONS = ['.content', '.brand-info', '.footer'];
  var savedRange = null;

  function setEditableRegions(on){
    EDITABLE_REGIONS.forEach(function(sel){
      var el = document.querySelector(sel);
      if(el){
        if(on) el.setAttribute('contenteditable', 'true');
        else el.removeAttribute('contenteditable');
      }
    });
  }

  function isOn(){
    return document.body.classList.contains('custom-edit-on');
  }

  function turnOn(){
    document.body.classList.add('custom-edit-on');
    setEditableRegions(true);
    if(toggleBtn) toggleBtn.classList.add('active');
    if(toggleLabel) toggleLabel.textContent = 'Exit Content Editor';
    if(editHint) editHint.style.display = '';
  }

  function turnOff(){
    document.body.classList.remove('custom-edit-on');
    setEditableRegions(false);
    if(toggleBtn) toggleBtn.classList.remove('active');
    if(toggleLabel) toggleLabel.textContent = 'Content Editor';
    if(editHint) editHint.style.display = 'none';
  }

  if(toggleBtn) toggleBtn.addEventListener('click', function(){
    if(isOn()) turnOff(); else turnOn();
  });

  document.addEventListener('selectionchange', function(){
    if(!isOn()) return;
    var sel = window.getSelection();
    if(sel && sel.rangeCount > 0){
      var range = sel.getRangeAt(0);
      var container = range.commonAncestorContainer;
      var el = container.nodeType === 1 ? container : container.parentElement;
      if(el && el.closest('.page')) savedRange = range.cloneRange();
    }
  });

  function restoreSelection(){
    if(!savedRange) return;
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(savedRange);
  }

  function runCommand(cmd, value){
    restoreSelection();
    document.execCommand(cmd, false, value || null);
  }

  document.getElementById('fmtBold').addEventListener('click', function(){ runCommand('bold'); });
  document.getElementById('fmtItalic').addEventListener('click', function(){ runCommand('italic'); });
  document.getElementById('fmtUnderline').addEventListener('click', function(){ runCommand('underline'); });
  document.getElementById('fmtFont').addEventListener('change', function(e){ runCommand('fontName', e.target.value); });
  document.getElementById('fmtSize').addEventListener('change', function(e){ runCommand('fontSize', e.target.value); });
  document.getElementById('fmtColor').addEventListener('input', function(e){ runCommand('foreColor', e.target.value); });

  document.getElementById('fmtDelete').addEventListener('click', function(){
    if(!savedRange) return;
    var node = savedRange.commonAncestorContainer;
    var el = node.nodeType === 1 ? node : node.parentElement;
    if(!el) return;
    var line = el.closest('p, .details-box .row, .footer-item, div > b, .pullquote') || el;
    if(line && line !== document.querySelector('.content') && line.parentElement){
      line.parentElement.removeChild(line);
    }
    savedRange = null;
  });

  // Multi-page documents (Agreement Letter) repeat the header/logo per page,
  // so there's no single unique #brandLogoImg to bind - logo click-to-replace
  // simply isn't offered there.
  if(logoImg) logoImg.addEventListener('click', function(){
    if(!isOn()) return;
    logoFileInput.click();
  });

  if(logoFileInput) logoFileInput.addEventListener('change', function(e){
    var file = e.target.files && e.target.files[0];
    if(!file) return;
    var reader = new FileReader();
    reader.onload = function(ev){
      if(logoImg) logoImg.src = ev.target.result;
    };
    reader.readAsDataURL(file);
  });
})();

// ---- Custom Edit: add/delete/icon-swap (header/body/footer) ----
  function addHeaderLine(){
    var div = document.createElement('div');
    div.innerHTML = '<span class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"><path d="M12 22C12 22 19.5 15.2 19.5 9.5A7.5 7.5 0 0 0 4.5 9.5C4.5 15.2 12 22 12 22Z"/><circle cx="12" cy="9.5" r="2.75"/></svg></span> <span contenteditable="plaintext-only">New line</span><span class="row-delete" onclick="this.parentElement.remove()">&times;</span>';
    document.querySelector('.brand-details').insertBefore(div, document.querySelector('.add-header-line'));
    wireIconClick(div.querySelector('.icon'), HEADER_ICONS);
  }

  function addBodyLine(){
    var p = document.createElement('p');
    p.setAttribute('contenteditable','plaintext-only');
    p.textContent = 'New paragraph text.';
    var span = document.createElement('span');
    span.className = 'row-delete';
    span.innerHTML = '&times;';
    span.onclick = function(){ p.remove(); };
    p.appendChild(span);
    var addBtn = document.querySelector('.add-body-line');
    addBtn.parentElement.insertBefore(p, addBtn);
  }

  function addFooterItem(){
    var div = document.createElement('div');
    div.className = 'footer-item';
    div.innerHTML = '<div class="footer-icon"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1.6a8.9 8.9 0 0 0-8.9 8.9C3.1 17 11 22.6 11.35 22.85a1.1 1.1 0 0 0 1.3 0C13 22.6 20.9 17 20.9 10.5A8.9 8.9 0 0 0 12 1.6m0 12.05a3.15 3.15 0 1 1 0-6.3 3.15 3.15 0 0 1 0 6.3"/></svg></div><div class="footer-text" contenteditable="plaintext-only">New line</div><div class="row-delete" onclick="this.parentElement.remove()">&times;</div>';
    var addBtn = document.querySelector('.add-footer-item');
    addBtn.parentElement.insertBefore(div, addBtn);
    wireIconClick(div.querySelector('.footer-icon'), FOOTER_ICONS);
  }

  var HEADER_ICONS = {
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"><path d="M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3C3 13.4 10.6 21 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4-2 2a15 15 0 0 1-5.4-5.4l2-2z"/></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"><rect x="2.5" y="5.5" width="19" height="13"/><path d="M2.5 5.5 12 13l9.5-7.5"/></svg>',
    location: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"><path d="M12 22C12 22 19.5 15.2 19.5 9.5A7.5 7.5 0 0 0 4.5 9.5C4.5 15.2 12 22 12 22Z"/><circle cx="12" cy="9.5" r="2.75"/></svg>',
    globe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25"><circle cx="12" cy="12" r="9.5"/><ellipse cx="12" cy="12" rx="4.2" ry="9.5"/><path d="M2.5 12h19M4.2 6.5h15.6M4.2 17.5h15.6"/></svg>'
  };

  var FOOTER_ICONS = {
    phone: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8.6 2.5H4.8A2.8 2.8 0 0 0 2 5.3C2 14 10 22 18.7 22a2.8 2.8 0 0 0 2.8-2.8v-3.8a1 1 0 0 0-.68-.95l-4.2-1.4a1 1 0 0 0-1.03.24l-1.6 1.6a14 14 0 0 1-4.18-4.18l1.6-1.6a1 1 0 0 0 .24-1.03l-1.4-4.2a1 1 0 0 0-.95-.68z"/></svg>',
    globe: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1.8a10.2 10.2 0 1 0 0 20.4 10.2 10.2 0 0 0 0-20.4M3.6 12.9h3.3c.1 2.1.5 4.1 1.2 5.7a8.5 8.5 0 0 1-4.5-5.7m3.3-1.8H3.6a8.5 8.5 0 0 1 4.5-5.7c-.7 1.6-1.1 3.6-1.2 5.7m4.2 9.3c-1-1-2.1-3.6-2.2-8.1h4.4c-.1 4.5-1.2 7.1-2.2 8.1m-2.2-9.9c.1-4.5 1.2-7.1 2.2-8.1 1 1 2.1 3.6 2.2 8.1zm7.2 0c-.1-2.1-.5-4.1-1.2-5.7a8.5 8.5 0 0 1 4.5 5.7zm-1.2 7.5c.7-1.6 1.1-3.6 1.2-5.7h3.3a8.5 8.5 0 0 1-4.5 5.7"/></svg>',
    location: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1.6a8.9 8.9 0 0 0-8.9 8.9C3.1 17 11 22.6 11.35 22.85a1.1 1.1 0 0 0 1.3 0C13 22.6 20.9 17 20.9 10.5A8.9 8.9 0 0 0 12 1.6m0 12.05a3.15 3.15 0 1 1 0-6.3 3.15 3.15 0 0 1 0 6.3"/></svg>'
  };

  // Superseded by the full Modern Corporate icon picker (openIconPicker) -
  // kept as a thin wrapper so existing call sites (which still pass an
  // unused iconSet arg) don't need to change.
  function showIconPicker(iconSpan){
    openIconPicker(iconSpan);
  }

  function wireIconClick(el, iconSet){
    if(!el) return;
    el.addEventListener('click', function(e){
      if(!document.body.classList.contains('custom-edit-on')) return;
      e.stopPropagation();
      showIconPicker(el, iconSet);
    });
  }

  document.querySelectorAll('.brand-details .icon').forEach(function(el){
    wireIconClick(el, HEADER_ICONS);
  });
  document.querySelectorAll('.footer-icon').forEach(function(el){
    wireIconClick(el, FOOTER_ICONS);
  });

// ---- Design Customizer ----
function dzToggleDrawer(){ document.getElementById('dzDrawer').classList.toggle('open'); }
function dzToggleSection(id){
  const el = document.getElementById(id);
  const willOpen = !el.classList.contains('open');
  if(el.classList.contains('pinned')){
    el.classList.toggle('open', willOpen);
    return;
  }
  document.querySelectorAll('.dz-section:not(.pinned)').forEach(s => s.classList.remove('open'));
  if(willOpen) el.classList.add('open');
}
function dzSetVar(varName, value, el){
  document.documentElement.style.setProperty(varName, value);
  if(el){
    const group = el.closest('.dz-swatches') || el.closest('.dz-aligngroup');
    if(group) group.querySelectorAll('.dz-swatch, .dz-alignbtn').forEach(s=>s.classList.remove('sel'));
    if(el.classList) el.classList.add('sel');
  }
}
const dzDefaults = {
  header: {
    '--header-bg':'#0c2e23','--header-font':"'Poppins',sans-serif",'--header-align':'flex-end',
    '--title-font':"'Public Sans', sans-serif",'--title-color':'#0c7a52',
    '--contact-text-color':'#9fd0b8','--phone-pill-bg':'#00e08a'
  },
  body: {'--body-font':"'Inter', Arial, sans-serif",'--pullquote-bg':'#f4fbf7'},
  details: {'--details-bg':'#f6fbf8'},
  footer: {
    '--footer-bg':'#0c2e23','--footer-text-color':'#9fd0b8',
    '--footer-icon-bg':'#00e08a','--footer-font':"'Inter', Arial, sans-serif"
  },
  textformat: {'--body-line-height':'1.62','--body-border-style':'none'}
};
function dzResetSection(key){
  const vars = dzDefaults[key];
  Object.keys(vars).forEach(v => document.documentElement.style.setProperty(v, vars[v]));
}

// ---- Content Persistence (candidate details, Custom Edit changes, Design Customizer choices) ----
(function(){
  var CONTENT_KEY = 'erudienceLetterContent_' + PAGE_ID;
  var DESIGN_KEY = 'erudienceDesignVars_' + PAGE_ID;
  var DESIGN_VARS = ['--header-bg','--footer-bg','--pullquote-bg','--details-bg','--body-font','--header-font','--header-align',
    '--body-align','--body-line-height','--body-font-color','--body-highlight-color','--body-border-style',
    '--title-font','--title-color','--contact-text-color','--phone-pill-bg',
    '--footer-text-color','--footer-icon-bg','--footer-font'];
  var saveTimer = null;

  // Multi-page documents (Agreement Letter's 2 pages) repeat .content /
  // .brand-details / .footer once per page, so every save/restore below
  // works over the full NodeList (indexed by page order) rather than just
  // the first match. `asList` upgrades an older single-page save (a plain
  // string) so it doesn't break when read back on a page like this one.
  function asList(v){ return Array.isArray(v) ? v : (v == null ? [] : [v]); }

  function getContentBodyHTML(content){
    var closing = content.querySelector('#closingBlock');
    var html = '';
    Array.prototype.forEach.call(content.children, function(el){
      if(el !== closing) html += el.outerHTML;
    });
    return html;
  }

  function saveContent(){
    try{
      var brandDetailsEls = document.querySelectorAll('.brand-details');
      var contentEls = document.querySelectorAll('.content');
      var footerEls = document.querySelectorAll('.footer');
      localStorage.setItem(CONTENT_KEY, JSON.stringify({
        brandDetails: Array.prototype.map.call(brandDetailsEls, function(el){ return el.innerHTML; }),
        contentBody: Array.prototype.map.call(contentEls, getContentBodyHTML),
        footer: Array.prototype.map.call(footerEls, function(el){ return el.innerHTML; })
      }));
    }catch(e){}
  }

  function debounceSaveContent(){
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveContent, 400);
  }

  function restoreContent(){
    try{
      var saved = JSON.parse(localStorage.getItem(CONTENT_KEY));
      if(!saved) return;

      var brandDetailsList = asList(saved.brandDetails);
      var footerList = asList(saved.footer);
      var contentBodyList = asList(saved.contentBody);

      document.querySelectorAll('.brand-details').forEach(function(el, i){
        if(brandDetailsList[i] != null) el.innerHTML = brandDetailsList[i];
      });
      document.querySelectorAll('.footer').forEach(function(el, i){
        if(footerList[i] != null) el.innerHTML = footerList[i];
      });

      document.querySelectorAll('.content').forEach(function(content, i){
        var bodyHTML = contentBodyList[i];
        if(bodyHTML == null) return;
        var closing = content.querySelector('#closingBlock');
        Array.prototype.slice.call(content.children).forEach(function(el){
          if(el !== closing) content.removeChild(el);
        });
        var temp = document.createElement('div');
        temp.innerHTML = bodyHTML;
        Array.prototype.slice.call(temp.children).forEach(function(el){
          if(closing) content.insertBefore(el, closing);
          else content.appendChild(el);
        });
      });

      // innerHTML replacement drops addEventListener-based handlers (icon click popovers) -
      // inline onclick attributes (delete "x", add-line/add-item) survive innerHTML round-trips fine.
      document.querySelectorAll('.brand-details .icon').forEach(function(el){ wireIconClick(el, HEADER_ICONS); });
      document.querySelectorAll('.footer-icon').forEach(function(el){ wireIconClick(el, FOOTER_ICONS); });
    }catch(e){}
  }

  function saveDesignVars(){
    try{
      var vals = {};
      DESIGN_VARS.forEach(function(p){
        var v = document.documentElement.style.getPropertyValue(p);
        if(v) vals[p] = v;
      });
      localStorage.setItem(DESIGN_KEY, JSON.stringify(vals));
    }catch(e){}
  }

  function syncDesignUI(vars){
    Object.keys(vars).forEach(function(varName){
      var value = vars[varName];
      document.querySelectorAll('.dz-swatch[onclick*="' + varName + '"], .dz-alignbtn[onclick*="' + varName + '"]').forEach(function(el){
        var onclickAttr = el.getAttribute('onclick') || '';
        if(onclickAttr.indexOf("'" + value + "'") !== -1){
          var group = el.closest('.dz-swatches') || el.closest('.dz-aligngroup');
          if(group) group.querySelectorAll('.dz-swatch, .dz-alignbtn').forEach(function(s){ s.classList.remove('sel'); });
          el.classList.add('sel');
        }
      });
      document.querySelectorAll('select[onchange*="' + varName + '"]').forEach(function(sel){
        var hasOption = Array.prototype.some.call(sel.options, function(o){ return o.value === value; });
        if(hasOption) sel.value = value;
      });
      document.querySelectorAll('input[type="range"][oninput*="' + varName + '"]').forEach(function(range){
        range.value = value;
      });
    });
  }

  function restoreDesignVars(){
    try{
      var saved = JSON.parse(localStorage.getItem(DESIGN_KEY));
      if(!saved) return;
      Object.keys(saved).forEach(function(p){
        document.documentElement.style.setProperty(p, saved[p]);
      });
      syncDesignUI(saved);
    }catch(e){}
  }

  restoreContent();
  restoreDesignVars();

  var observer = new MutationObserver(debounceSaveContent);
  ['.brand-details', '.content', '.footer'].forEach(function(sel){
    document.querySelectorAll(sel).forEach(function(el){
      observer.observe(el, { childList: true, subtree: true, characterData: true });
    });
  });

  var origDzSetVar = window.dzSetVar;
  window.dzSetVar = function(varName, value, el){
    origDzSetVar(varName, value, el);
    saveDesignVars();
  };
  var origDzResetSection = window.dzResetSection;
  window.dzResetSection = function(key){
    origDzResetSection(key);
    saveDesignVars();
  };
})();

// ---- Mobile tap-to-reveal delete buttons (Custom Edit) ----
(function(){
  var ROW_SELECTOR = '.brand-details > div:not(.add-header-line), .content > p, .content > h3, .footer-item, .details-box .row';

  document.addEventListener('click', function(e){
    if(!document.body.classList.contains('custom-edit-on')) return;
    if(e.target.closest('.row-delete')) return;
    var row = e.target.closest(ROW_SELECTOR);
    if(!row) return;
    var wasShown = row.classList.contains('tap-show');
    document.querySelectorAll('.tap-show').forEach(function(el){ el.classList.remove('tap-show'); });
    if(!wasShown) row.classList.add('tap-show');
  });

  var toggleBtn = document.getElementById('customEditToggle');
  if(toggleBtn){
    toggleBtn.addEventListener('click', function(){
      if(!document.body.classList.contains('custom-edit-on')){
        document.querySelectorAll('.tap-show').forEach(function(el){ el.classList.remove('tap-show'); });
      }
    });
  }
})();

// ---- Reset Letter button ----
(function(){
  var resetBtn = document.getElementById('resetLetterBtn');
  if(!resetBtn) return;
  resetBtn.addEventListener('click', function(){
    var ok = window.confirm('This will erase all your edits (text, added/removed lines, colors, signature) and reload the letter with its original default content. This cannot be undone. Continue?');
    if(!ok) return;
    try{
      localStorage.removeItem('erudienceLetterContent_' + PAGE_ID);
      localStorage.removeItem('erudienceDesignVars_' + PAGE_ID);
      localStorage.removeItem('erudienceSignatureSettings_' + PAGE_ID);
    }catch(e){}
    window.location.reload();
  });
})();

// ---- Text Formatting: compact icon toolbar (V3, per-selection rich text) ----
var tfSavedRange = null;
var tfUnderlineStyle = 'solid';
var tfUnderlineColor = '#1c2a25';

function tfRangeInContent(range){
  if(!range) return false;
  var node = range.commonAncestorContainer;
  var el = node.nodeType === 1 ? node : node.parentElement;
  return !!(el && el.closest('.content'));
}

// Chrome's justify* commands sometimes wrap a paragraph's content in a new
// inner <div style="text-align:..."> instead of styling the <p> itself -
// a <div> inside a <p> is invalid HTML and would come back malformed after
// a save/reload round-trip (innerHTML is re-parsed as HTML). Flatten it.
function tfFixJustifyWrapper(command){
  if(['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'].indexOf(command) === -1) return;
  document.querySelectorAll('.content p > div[style*="text-align"]').forEach(function(div){
    var p = div.parentElement;
    p.style.textAlign = div.style.textAlign;
    while(div.firstChild) p.insertBefore(div.firstChild, div);
    p.removeChild(div);
  });
}

function tfExec(command, btn){
  document.execCommand(command, false, null);
  tfFixJustifyWrapper(command);
  if(btn) btn.classList.toggle('on', document.queryCommandState(command));
}

// Turns the current paragraph into a heading (matching the letter's existing
// section-label style) or back into a plain paragraph. Block-level, so it
// only needs the cursor inside the paragraph - no text selection required.
function tfToggleHeading(btn){
  var isHeading = document.queryCommandValue('formatBlock').toLowerCase() === 'h3';
  document.execCommand('formatBlock', false, isHeading ? 'p' : 'h3');
  if(btn) btn.classList.toggle('on', !isHeading);
}

function tfRestoreRangeIfAny(){
  if(!tfSavedRange) return false;
  var sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(tfSavedRange);
  return true;
}

function tfExecPanel(command, btn){
  tfRestoreRangeIfAny();
  tfExec(command, btn);
}

function tfShowPanel(kind, btn){
  var sel = window.getSelection();
  var range = sel.rangeCount ? sel.getRangeAt(0) : null;
  tfSavedRange = (range && tfRangeInContent(range)) ? range.cloneRange() : null;
  document.querySelectorAll('.tf-btn').forEach(function(b){ b.classList.remove('tf-active'); });
  if(btn) btn.classList.add('tf-active');
  tfUnderlineStyle = 'solid';
  tfUnderlineColor = '#1c2a25';
  document.getElementById('tfPanel').innerHTML = tfRenderPanel(kind);
}

function tfRenderPanel(kind){
  var hasRange = !!tfSavedRange;
  var hasSelection = hasRange && !tfSavedRange.collapsed;
  var noSelectionHint = '<div class="tf-hint">Select some text first</div>';

  if(kind === 'underline'){
    return '' +
      '<div class="dz-ctrl-label">UNDERLINE STYLE</div>' +
      '<div class="tf-optrow">' +
        '<div class="tf-opt sel" onclick="tfSelectUnderlineStyle(\'solid\', this)">Single</div>' +
        '<div class="tf-opt" onclick="tfSelectUnderlineStyle(\'double\', this)">Double</div>' +
        '<div class="tf-opt" onclick="tfSelectUnderlineStyle(\'dotted\', this)">Dotted</div>' +
        '<div class="tf-opt" onclick="tfSelectUnderlineStyle(\'dashed\', this)">Dashed</div>' +
        '<div class="tf-opt" onclick="tfSelectUnderlineStyle(\'wavy\', this)">Wavy</div>' +
      '</div>' +
      '<div class="dz-ctrl-label" style="margin-top:10px;">COLOUR</div>' +
      '<div class="dz-swatches">' +
        '<div class="dz-swatch sel" style="background:#1c2a25" onclick="tfSelectUnderlineColor(\'#1c2a25\', this)"></div>' +
        '<div class="dz-swatch" style="background:#0c7a52" onclick="tfSelectUnderlineColor(\'#0c7a52\', this)"></div>' +
        '<div class="dz-swatch" style="background:#c0392b" onclick="tfSelectUnderlineColor(\'#c0392b\', this)"></div>' +
        '<input type="color" class="dz-swatch" value="#1c2a25" onchange="tfSelectUnderlineColor(this.value, this)" style="padding:0;border:1px solid #e3e8e5">' +
      '</div>' +
      '<button type="button" class="tf-apply-btn"' + (hasSelection ? '' : ' disabled') + ' onclick="tfApplyUnderline()">Apply underline</button>' +
      (hasSelection ? '' : noSelectionHint);
  }

  if(kind === 'fontcolor' || kind === 'highlight'){
    var label = kind === 'fontcolor' ? 'FONT COLOUR' : 'HIGHLIGHT COLOUR';
    var presets = kind === 'fontcolor'
      ? ['#1c2a25', '#0c2e23', '#c0392b']
      : ['#fff59d', '#c6f6d5', '#bee3f8'];
    var swatchHtml = presets.map(function(c){
      return '<div class="dz-swatch" style="background:' + c + '" onclick="tfApplyColor(\'' + kind + '\',\'' + c + '\')"></div>';
    }).join('');
    return '<div class="dz-ctrl-label">' + label + '</div>' +
      '<div class="dz-swatches">' + swatchHtml +
      '<input type="color" class="dz-swatch" value="#000000" onchange="tfApplyColor(\'' + kind + '\', this.value)" style="padding:0;border:1px solid #e3e8e5">' +
      '</div>' + (hasSelection ? '' : noSelectionHint);
  }

  if(kind === 'align'){
    return '<div class="dz-ctrl-label">ALIGN PARAGRAPH</div>' +
      '<div class="tf-optrow">' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfExecPanel(\'justifyLeft\', this)">Left</div>' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfExecPanel(\'justifyCenter\', this)">Center</div>' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfExecPanel(\'justifyRight\', this)">Right</div>' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfExecPanel(\'justifyFull\', this)">Justify</div>' +
      '</div>' +
      (hasRange ? '' : '<div class="tf-hint">Click inside a paragraph first</div>');
  }

  if(kind === 'case'){
    return '<div class="dz-ctrl-label">CHANGE CASE</div>' +
      '<div class="tf-optrow">' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfApplyCase(\'uppercase\')">ALL CAPS</div>' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfApplyCase(\'smallcaps\')">Small caps</div>' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfApplyCase(\'sentence\')">Sentence case</div>' +
        '<div class="tf-btn" style="width:auto;padding:0 10px;" onclick="tfApplyCase(\'lower\')">lowercase</div>' +
      '</div>' + (hasSelection ? '' : noSelectionHint);
  }

  return '';
}

function tfSelectUnderlineStyle(style, el){
  tfUnderlineStyle = style;
  var group = el.parentElement;
  group.querySelectorAll('.tf-opt').forEach(function(o){ o.classList.remove('sel'); });
  el.classList.add('sel');
}

function tfSelectUnderlineColor(color, el){
  tfUnderlineColor = color;
  var group = el.parentElement;
  group.querySelectorAll('.dz-swatch').forEach(function(s){ s.classList.remove('sel'); });
  if(el.classList) el.classList.add('sel');
}

// Wraps just the in-range portion of every text node the range touches, each
// in its own <span> - unlike range.surroundContents()/extractContents(), this
// stays correct when the range crosses paragraph (<p>) boundaries, since it
// never tries to stuff a block element inside an inline <span>.
function tfGetIntersectingTextNodes(range){
  var root = range.commonAncestorContainer;
  // A TreeWalker only visits DESCENDANTS of its root - if the range sits
  // entirely inside one text node, that text node itself is the common
  // ancestor and has no children, so the walker would find nothing.
  if(root.nodeType === 3) return [root];
  var textNodes = [];
  var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: function(node){
      return range.intersectsNode(node) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });
  var node;
  while(node = walker.nextNode()) textNodes.push(node);
  return textNodes;
}

function tfWrapRangeText(range, styleFn){
  var textNodes = tfGetIntersectingTextNodes(range);

  textNodes.forEach(function(tn){
    var start = (tn === range.startContainer) ? range.startOffset : 0;
    var end = (tn === range.endContainer) ? range.endOffset : tn.length;
    if(start >= end) return;
    if(end < tn.length) tn.splitText(end);
    var middle = (start > 0) ? tn.splitText(start) : tn;
    if(!middle.data) return;
    var span = document.createElement('span');
    styleFn(span);
    middle.parentNode.insertBefore(span, middle);
    span.appendChild(middle);
  });
}

function tfApplyUnderline(){
  if(!tfRestoreRangeIfAny()) return;
  var sel = window.getSelection();
  if(sel.rangeCount === 0) return;
  var range = sel.getRangeAt(0);
  if(range.collapsed) return;
  tfWrapRangeText(range, function(span){
    span.style.textDecorationLine = 'underline';
    span.style.textDecorationStyle = tfUnderlineStyle;
    span.style.textDecorationColor = tfUnderlineColor;
  });
  sel.removeAllRanges();
  document.getElementById('tfPanel').innerHTML = '';
}

function tfApplyColor(kind, color){
  if(!tfRestoreRangeIfAny()) return;
  var sel = window.getSelection();
  if(sel.rangeCount === 0 || sel.getRangeAt(0).collapsed) return;
  document.execCommand(kind === 'highlight' ? 'hiliteColor' : 'foreColor', false, color);
}

function tfApplyCase(kind){
  if(!tfRestoreRangeIfAny()) return;
  var sel = window.getSelection();
  if(sel.rangeCount === 0) return;
  var range = sel.getRangeAt(0);
  if(range.collapsed) return;

  if(kind === 'uppercase' || kind === 'smallcaps'){
    tfWrapRangeText(range, function(span){
      if(kind === 'uppercase') span.style.textTransform = 'uppercase';
      else span.style.fontVariant = 'small-caps';
    });
    sel.removeAllRanges();
  } else {
    var textNodes = tfGetIntersectingTextNodes(range);
    textNodes.forEach(function(tn){
      var start = (tn === range.startContainer) ? range.startOffset : 0;
      var end = (tn === range.endContainer) ? range.endOffset : tn.length;
      if(start >= end) return;
      if(end < tn.length) tn.splitText(end);
      var middle = (start > 0) ? tn.splitText(start) : tn;
      middle.data = kind === 'lower' ? middle.data.toLowerCase() : tfToSentenceCase(middle.data);
    });
    sel.removeAllRanges();
  }
}

function tfToSentenceCase(str){
  var lower = str.toLowerCase();
  return lower.replace(/(^\s*[a-z]|[.!?]\s+[a-z])/g, function(m){ return m.toUpperCase(); });
}

document.addEventListener('selectionchange', function(){
  document.querySelectorAll('.tf-btn[data-cmd]').forEach(function(btn){
    var cmd = btn.dataset.cmd;
    try{ btn.classList.toggle('on', document.queryCommandState(cmd)); }catch(e){}
  });
  var headingBtn = document.getElementById('tfHeadingBtn');
  if(headingBtn){
    try{ headingBtn.classList.toggle('on', document.queryCommandValue('formatBlock').toLowerCase() === 'h3'); }catch(e){}
  }
});



// ---- Icon Picker (Modern Corporate: sidebar category list) ----
const ICON_LIBRARY = {
  'phone': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3C3 13.4 10.6 21 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4-2 2a15 15 0 0 1-5.4-5.4l2-2z"/><path d="M18.7 3.5v3"/><circle class="node" cx="18.7" cy="3" r="1.3" stroke="none"/></svg>', category: 'Contact' },
  'email': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="2.5" y="5.5" width="19" height="13" rx="1"/><path d="M2.5 5.5 12 13l9.5-7.5"/><path d="M12 13v4.5"/><circle class="node" cx="12" cy="18.5" r="1.3" stroke="none"/></svg>', category: 'Contact' },
  'location': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M12 22C12 22 19.5 15.2 19.5 9.5A7.5 7.5 0 0 0 4.5 9.5C4.5 15.2 12 22 12 22Z"/><circle cx="12" cy="9.5" r="2.75"/><circle class="node" cx="12" cy="9.5" r="1.3" stroke="none"/></svg>', category: 'Contact' },
  'website': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5A15 15 0 0 1 12 21.5"/><circle class="node" cx="12" cy="21.5" r="1.3" stroke="none"/></svg>', category: 'Contact' },
  'offer-letter': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h9l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M9 13h6M9 17h4"/><path d="M15 3v5h5"/><circle class="node" cx="15" cy="8" r="1.3" stroke="none"/></svg>', category: 'Documents' },
  'agreement': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/><path d="M12 3v1.2"/><circle class="node" cx="12" cy="2.3" r="1.2" stroke="none"/></svg>', category: 'Documents' },
  'termination': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/><path d="M19.5 4.5l.7.7"/><circle class="node" cx="20.9" cy="5.9" r="1.2" stroke="none"/></svg>', category: 'Documents' },
  'proposal': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"><path d="M4 4h13l3 3v13H4z"/><path d="M8 9h8M8 13h5"/><path d="M17 4v3h3"/><circle class="node" cx="20" cy="4" r="1.2" stroke="none"/></svg>', category: 'Documents' },
  'showcase': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/><path d="M19 7v-2h-2"/><circle class="node" cx="20" cy="4" r="1.2" stroke="none"/></svg>', category: 'Documents' },
  'invoice': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 8h8M8 12h8M8 16h5"/><path d="M17 16v2"/><circle class="node" cx="17" cy="19" r="1.2" stroke="none"/></svg>', category: 'Documents' },
  'edit': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/><path d="M14.5 6.5l3 3"/><circle class="node" cx="19.3" cy="4.7" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'add': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M12 6v12M6 12h12"/><circle class="node" cx="12" cy="12" r="1.3" stroke="none" opacity="0"/><circle class="node" cx="18" cy="6" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'delete': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/><path d="M12 11v6"/><circle class="node" cx="12" cy="18" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'print': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/><path d="M18 4v2"/><circle class="node" cx="18" cy="2.5" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'menu': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M3 12h18M3 18h18"/><path d="M21 6v-2"/><circle class="node" cx="21" cy="3" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'close': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/><circle class="node" cx="18" cy="6" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'confirm': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/><circle class="node" cx="20" cy="6" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'reset': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><circle class="node" cx="3" cy="4" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'pending': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/><circle class="node" cx="12" cy="12" r="1.2" stroke="none"/></svg>', category: 'Status & Future' },
  'approved': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/><circle class="node" cx="22" cy="4" r="1.2" stroke="none"/></svg>', category: 'Status & Future' },
  'warning': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01"/><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><circle class="node" cx="12" cy="17" r="1.1" stroke="none"/></svg>', category: 'Status & Future' },
  'upload': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/><circle class="node" cx="12" cy="3" r="1.2" stroke="none"/></svg>', category: 'Status & Future' },
  'ai-magic': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.4 7.2H22l-6 4.4 2.3 7.1L12 16.3l-6.3 4.4 2.3-7.1-6-4.4h7.6z"/><circle class="node" cx="12" cy="9.6" r="1.3" stroke="none"/></svg>', category: 'Status & Future' },
  'profile': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/><circle class="node" cx="12" cy="8" r="1.2" stroke="none"/></svg>', category: 'Status & Future' },
  'search': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/><circle class="node" cx="21" cy="21" r="1.2" stroke="none"/></svg>', category: 'Status & Future' },
  'notification': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a6 6 0 0 0-6 6c0 5-2 6-2 6h16s-2-1-2-6a6 6 0 0 0-6-6z"/><path d="M10 20a2 2 0 0 0 4 0"/><circle class="node" cx="12" cy="2" r="1.2" stroke="none"/></svg>', category: 'Status & Future' },
  'download': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5M12 15V3"/><circle class="node" cx="12" cy="3" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'duplicate': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="1.5"/><path d="M5 15V4.5A1.5 1.5 0 0 1 6.5 3H15"/><circle class="node" cx="6.5" cy="3" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'share': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.6M8.2 13.2l7.6 4.6"/><circle class="node" cx="18" cy="5" r="1" stroke="none"/></svg>', category: 'Actions' },
  'settings': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/><circle class="node" cx="20.5" cy="6.5" r="1" stroke="none"/></svg>', category: 'Actions' },
  'calendar': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><circle class="node" cx="16" cy="2" r="1.2" stroke="none"/></svg>', category: 'Scheduling' },
  'confidential': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"><rect x="4" y="11" width="16" height="10" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><circle class="node" cx="12" cy="16" r="1.2" stroke="none"/></svg>', category: 'Security' },
  'preview': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/><circle class="node" cx="20" cy="8" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'save': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/><circle class="node" cx="17" cy="13" r="1.2" stroke="none"/></svg>', category: 'Actions' },
  'colour-palette': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.9 0 1.6-.7 1.6-1.7 0-.4-.2-.8-.4-1.1-.3-.3-.4-.7-.4-1.1a1.6 1.6 0 0 1 1.7-1.7h2c3 0 5.5-2.5 5.5-5.5C22 6 17.5 2 12 2z"/><circle cx="6.5" cy="11.5" r="1"/><circle cx="9.5" cy="7.5" r="1"/><circle cx="14.5" cy="7.5" r="1"/><circle class="node" cx="17.5" cy="10.5" r="1.2" stroke="none"/></svg>', category: 'Background / Theme Edit' },
  'fill-paint-bucket': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 11l-6-6-9 9 6 6z"/><path d="M5 14l-2 4a2 2 0 0 0 2 2h4l-4-6z"/><path d="M13 5l2-2 6 6-2 2"/><circle class="node" cx="19" cy="3" r="1.2" stroke="none"/></svg>', category: 'Background / Theme Edit' },
  'theme': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2a7.5 7.5 0 1 0 5.4 12.7c.5-.5 1.3-.2 1.4.5.3 1.8 1.8 3.3 3.7 2.8"/><path d="M9.5 2c1 2 1 5 0 7"/><circle class="node" cx="9.5" cy="2" r="1.2" stroke="none"/></svg>', category: 'Background / Theme Edit' },
  'background-layout': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/><circle class="node" cx="17" cy="17" r="1.2" stroke="none"/></svg>', category: 'Background / Theme Edit' },
  'background-image': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 16l5-5 4 4 5-6 4 5"/><circle class="node" cx="17" cy="9" r="1.3" stroke="none"/></svg>', category: 'Background / Theme Edit' },
  'contrast': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12a8 8 0 1 1 16 0"/><path d="M4 12a8 8 0 0 0 16 0"/><path d="M12 4v16"/><circle class="node" cx="12" cy="4" r="1.2" stroke="none"/></svg>', category: 'Background / Theme Edit' },
  'folder': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/><circle class="node" cx="19" cy="5" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'attachment': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21.4 11.1l-9 9a4 4 0 0 1-5.7-5.7l9-9a2.7 2.7 0 0 1 3.8 3.8l-9 9a1.3 1.3 0 0 1-1.9-1.9l8.1-8.1"/><circle class="node" cx="21.4" cy="4.9" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'link': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.5.4l2-2a5 5 0 0 0-7-7l-1.2 1.1"/><path d="M14 11a5 5 0 0 0-7.5-.4l-2 2a5 5 0 0 0 7 7l1.1-1.1"/><circle class="node" cx="20.5" cy="3.5" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'tag-label': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.6 12.6L13 20a2 2 0 0 1-2.8 0l-7-7a2 2 0 0 1 0-2.8L11 2h7a2 2 0 0 1 2 2v7l.6.6z"/><circle cx="14.5" cy="7.5" r="1.3"/><circle class="node" cx="18" cy="4" r="1" stroke="none"/></svg>', category: 'File & Organisation' },
  'bookmark': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/><circle class="node" cx="19" cy="3" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'grid-view': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><circle class="node" cx="17.5" cy="17.5" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'list-view': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/><circle class="node" cx="4" cy="6" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'filter': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 3H2l8 9.5V19l4 2v-8.5z"/><circle class="node" cx="20" cy="2" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'sort': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M7 12h10M11 18h2"/><circle class="node" cx="21" cy="6" r="1.2" stroke="none"/></svg>', category: 'File & Organisation' },
  'back': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/><circle class="node" cx="9" cy="12" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'forward': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/><circle class="node" cx="15" cy="12" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'history': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 8v4l2.5 2.5"/><circle class="node" cx="3" cy="4" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'team': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/><circle class="node" cx="23" cy="3" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'add-user': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><path d="M20 8v6M23 11h-6"/><circle class="node" cx="20" cy="8" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'bold': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 0 1 0 8H6zM6 12h9a4 4 0 0 1 0 8H6z"/></svg>', category: 'Text Formatting' },
  'italic': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 4h-9M14 20H5M15 4L9 20"/></svg>', category: 'Text Formatting' },
  'underline': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v6a6 6 0 0 0 12 0V4M4 20h16"/></svg>', category: 'Text Formatting' },
  'strikethrough': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4H18M12 4v16M4 20h16"/></svg>', category: 'Text Formatting' },
  'align-left': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h10M4 18h13"/></svg>', category: 'Text Formatting' },
  'align-centre': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M7 12h10M5.5 18h13"/></svg>', category: 'Text Formatting' },
  'align-right': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M10 12h10M7 18h13"/></svg>', category: 'Text Formatting' },
  'justify': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>', category: 'Text Formatting' },
  'indent': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8l4 4-4 4M7 8H3M7 16H3M15 12H7"/></svg>', category: 'Text Formatting' },
  'outdent': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M7 8l-4 4 4 4M3 8h4M3 16h4M17 12H9"/></svg>', category: 'Text Formatting' },
  'quote': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/></svg>', category: 'Text Formatting' },
  'code': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/></svg>', category: 'Text Formatting' },
  'bullet-list': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="6" cy="18" r="2"/><path d="M11 6h9M11 12h9M11 18h9"/></svg>', category: 'Text Formatting' },
  'numbered-list': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M11 6h9M11 12h9M11 18h9M4 6h1v1H4zM4 12h1v1H4zM4 18h1v1H4z"/></svg>', category: 'Text Formatting' },
  'paragraph': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 12h12M6 6h12M6 18h8"/></svg>', category: 'Text Formatting' },
  'chat': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>', category: 'Communication' },
  'mail': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5.5" width="19" height="13" rx="1"/><path d="M2.5 5.5 12 13l9.5-7.5"/></svg>', category: 'Communication' },
  'message': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v12H8l-4 4z"/></svg>', category: 'Communication' },
  'phone-call': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3C3 13.4 10.6 21 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4-2 2a15 15 0 0 1-5.4-5.4l2-2z"/></svg>', category: 'Communication' },
  'video-call': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>', category: 'Communication' },
  'microphone': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/></svg>', category: 'Communication' },
  'mute': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M1 1l22 22"/><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/><path d="M17 16.95A7 7 0 0 1 5 12v-2M19 12v2a7 7 0 0 1-.11 1.23"/><path d="M12 19v4M8 23h8"/></svg>', category: 'Communication' },
  'call-history': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.362 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>', category: 'Communication' },
  'currency': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>', category: 'Finance & Invoice' },
  'percent': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>', category: 'Finance & Invoice' },
  'calculator': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="14" x2="16" y2="18"/><path d="M16 10h.01M12 10h.01M8 10h.01M12 14h.01M8 14h.01M12 18h.01M8 18h.01"/></svg>', category: 'Finance & Invoice' },
  'wallet': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/></svg>', category: 'Finance & Invoice' },
  'credit-card': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>', category: 'Finance & Invoice' },
  'bank': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M4 21V9l8-6 8 6v12M9 21v-6h6v6"/></svg>', category: 'Finance & Invoice' },
  'receipt': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2h16v20l-3-2-2 2-3-2-3 2-2-2-3 2z"/><path d="M8 8h8M8 12h8M8 16h4"/></svg>', category: 'Finance & Invoice' },
  'discount': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/><circle cx="12" cy="12" r="4"/></svg>', category: 'Finance & Invoice' },
  'bar-chart': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>', category: 'Charts & Data' },
  'pie-chart': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>', category: 'Charts & Data' },
  'line-chart': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg>', category: 'Charts & Data' },
  'trending-up': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>', category: 'Charts & Data' },
  'trending-down': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>', category: 'Charts & Data' },
  'table': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v18H3z"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>', category: 'Charts & Data' },
  'database': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>', category: 'Charts & Data' },
  'unlocked': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>', category: 'Security' },
  'shield': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 3v6c0 5-3.5 8.5-8 11-4.5-2.5-8-6-8-11V5z"/></svg>', category: 'Security' },
  'key': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"/><path d="M21 2l-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/></svg>', category: 'Security' },
  'fingerprint': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8 2 6 5 6 9c0 6 3 9 3 13M9 9a3 3 0 0 1 6 0c0 4-2 6-2 9M12 6a1 1 0 0 1 1 1c0 4-1.5 8-4 11"/></svg>', category: 'Security' },
  'hide': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M1 1l22 22"/><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/></svg>', category: 'Security' },
  'verified': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/><circle cx="12" cy="12" r="10"/></svg>', category: 'Security' },
  'sun': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/></svg>', category: 'Time & Alerts' },
  'moon': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>', category: 'Time & Alerts' },
  'timer': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M9 2h6M18 4l-1 1M6 4l1 1"/></svg>', category: 'Time & Alerts' },
  'clock': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>', category: 'Time & Alerts' },
  'alarm': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>', category: 'Time & Alerts' },
  'up': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>', category: 'Arrows & Direction' },
  'down': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>', category: 'Arrows & Direction' },
  'left': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>', category: 'Arrows & Direction' },
  'right': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>', category: 'Arrows & Direction' },
  'up-right': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>', category: 'Arrows & Direction' },
  'expand': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>', category: 'Arrows & Direction' },
  'collapse': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/></svg>', category: 'Arrows & Direction' },
  'refresh': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>', category: 'Arrows & Direction' },
  'swap': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 1l4 4-4 4M3 11V9a4 4 0 0 1 4-4h14M7 23l-4-4 4-4M21 13v2a4 4 0 0 1-4 4H3"/></svg>', category: 'Arrows & Direction' },
  'desktop': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>', category: 'Devices' },
  'mobile': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>', category: 'Devices' },
  'tablet': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>', category: 'Devices' },
  'camera': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>', category: 'Devices' },
  'image': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>', category: 'Devices' },
  'video': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>', category: 'Devices' },
  'like': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.8 1-1a5.5 5.5 0 0 0 0-7.6z"/></svg>', category: 'Social' },
  'thumbs-up': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.3a2 2 0 0 0 2-1.7l1.4-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>', category: 'Social' },
  'thumbs-down': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3M10 15v4a3 3 0 0 0 3 3l4-9V2H5.7a2 2 0 0 0-2 1.7l-1.4 9a2 2 0 0 0 2 2.3H10z"/></svg>', category: 'Social' },
  'flag': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>', category: 'Social' },
  'pdf-file': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><text x="7" y="18" font-size="6" fill="currentColor" stroke="none">PDF</text></svg>', category: 'Files & Formats' },
  'doc-file': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><text x="7" y="18" font-size="6" fill="currentColor" stroke="none">DOC</text></svg>', category: 'Files & Formats' },
  'image-file': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 15l2 2 4-4"/></svg>', category: 'Files & Formats' },
  'zip-file': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M10 12v6M14 12v6M10 15h4"/></svg>', category: 'Files & Formats' },
  'csv-file': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/></svg>', category: 'Files & Formats' },
  'draft': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12h8" stroke-dasharray="2 2"/></svg>', category: 'Status Extended' },
  'archived': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8v13H3V8M1 3h22v5H1zM10 12h4"/></svg>', category: 'Status Extended' },
  'published': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/><path d="M17 2l2 2 4-4" stroke-width="0"/></svg>', category: 'Status Extended' },
  'error': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>', category: 'Status Extended' },
  'info': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>', category: 'Status Extended' },
  'copy': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>', category: 'Editing Actions' },
  'paste': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>', category: 'Editing Actions' },
  'cut': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/><line x1="4" y1="4" x2="8.12" y2="8.12"/></svg>', category: 'Editing Actions' },
  'undo': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"/><path d="M3 13a9 9 0 1 0 3-7.7L3 7"/></svg>', category: 'Editing Actions' },
  'redo': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7v6h-6"/><path d="M21 13a9 9 0 1 1-3-7.7L21 7"/></svg>', category: 'Editing Actions' },
  'zoom-in': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>', category: 'Editing Actions' },
  'zoom-out': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>', category: 'Editing Actions' },
  'maximise': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/></svg>', category: 'Editing Actions' },
  'minimise': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3a2 2 0 0 1-2 2H3M21 8h-3a2 2 0 0 1-2-2V3M3 16h3a2 2 0 0 1 2 2v3M16 21v-3a2 2 0 0 1 2-2h3"/></svg>', category: 'Editing Actions' },
  'drag-handle': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="5" r="1"/><circle cx="15" cy="5" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="9" cy="19" r="1"/><circle cx="15" cy="19" r="1"/></svg>', category: 'Editing Actions' },
  'two-columns': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="18" rx="1"/><rect x="14" y="3" width="7" height="18" rx="1"/></svg>', category: 'Layout' },
  'two-rows': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="7" rx="1"/><rect x="3" y="14" width="18" height="7" rx="1"/></svg>', category: 'Layout' },
  'sidebar-left': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="18" rx="1"/><rect x="12" y="3" width="9" height="18" rx="1"/></svg>', category: 'Layout' },
  'sidebar-right': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="9" height="18" rx="1"/><rect x="14" y="3" width="7" height="18" rx="1"/></svg>', category: 'Layout' },
  'split-view': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="18" height="8" rx="1"/></svg>', category: 'Layout' },
  'building': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M6 21V7l6-4 6 4v14M10 9h.01M14 9h.01M10 13h.01M14 13h.01M10 17h.01M14 17h.01"/></svg>', category: 'Organisation' },
  'briefcase': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>', category: 'Organisation' },
  'handshake': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M11 21H4a2 2 0 0 1-2-2v-3.28a1 1 0 0 1 .89-1L11 14M13 21h7a2 2 0 0 0 2-2v-3.28a1 1 0 0 0-.89-1L13 14"/><circle cx="12" cy="8" r="5"/></svg>', category: 'Organisation' },
  'pulse-activity': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>', category: 'Organisation' },
  'square': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>', category: 'Shapes' },
  'circle': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/></svg>', category: 'Shapes' },
  'triangle': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l10 18H2z"/></svg>', category: 'Shapes' },
  'hexagon': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 3.5L22 12l-4.5 8.5h-11L2 12l4.5-8.5z"/></svg>', category: 'Shapes' },
  'star-shape': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3 7h7l-5.5 4.5L18.5 21 12 16.5 5.5 21l2-7.5L2 9h7z"/></svg>', category: 'Shapes' },
  'heart-shape': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-4.5-9.5-9C1 8 2.5 4 6.5 4c2.3 0 3.7 1.3 5.5 3.5C13.8 5.3 15.2 4 17.5 4 21.5 4 23 8 21.5 12c-2.5 4.5-9.5 9-9.5 9z"/></svg>', category: 'Shapes' },
  'calendar-grid': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/></svg>', category: 'Scheduling' },
  'deadline-urgent': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9z"/></svg>', category: 'Scheduling' },
  'duration': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>', category: 'Scheduling' },
  'schedule-confirmed': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M9 16l2 2 4-4"/></svg>', category: 'Scheduling' },
  'add-to-calendar': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></svg>', category: 'Scheduling' },
  'help': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>', category: 'Accessibility & Feedback' },
  'feedback-happy': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 15s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></svg>', category: 'Accessibility & Feedback' },
  'feedback-sad': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 16s-1.5-2-4-2-4 2-4 2M9 9h.01M15 9h.01"/></svg>', category: 'Accessibility & Feedback' },
  'checklist': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 4L12 14.01l-3-3"/><path d="M2 12l2 2 4-4M2 5l2 2 4-4"/></svg>', category: 'Accessibility & Feedback' },
  'task-complete': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>', category: 'Accessibility & Feedback' },
  'stack': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12c0 1.66-4.48 3-10 3S2 13.66 2 12"/><path d="M2 5v14c0 1.66 4.48 3 10 3s10-1.34 10-3V5"/><path d="M22 5c0 1.66-4.48 3-10 3S2 6.66 2 5s4.48-3 10-3 10 1.34 10 3z"/></svg>', category: 'Data & Storage' },
  'archive-box': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8"/><path d="M4 7V5a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v2"/></svg>', category: 'Data & Storage' },
  'cloud': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>', category: 'Data & Storage' },
  'cloud-storage': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>', category: 'Data & Storage' },
  'inbox': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>', category: 'Data & Storage' },
  'text-size': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7V4h16v3M9 20h6M12 4v16"/></svg>', category: 'Formatting Extra' },
  'sign-signature': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/><path d="M15 5l4 4"/></svg>', category: 'Formatting Extra' },
  'highlight-marker': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4L18.5 9.5a2.83 2.83 0 1 0-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>', category: 'Formatting Extra' },
  'eraser': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"/><line x1="16" y1="8" x2="2" y2="22"/><line x1="17.5" y1="15" x2="9" y2="15"/></svg>', category: 'Formatting Extra' },
  'draw': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>', category: 'Formatting Extra' },
  'notice': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>', category: 'Misc Utility' },
  'progress': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10"/><path d="M12 2v10l7-7"/></svg>', category: 'Misc Utility' },
  'sync': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4.9 4.9a10 10 0 0 0 0 14.2M19.1 4.9a10 10 0 0 1 0 14.2"/><circle cx="12" cy="12" r="3"/></svg>', category: 'Misc Utility' },
  'repeat': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 1 2.64 6.36L3 21"/><path d="M3 15v6h6"/></svg>', category: 'Misc Utility' },
  'loading': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12a8 8 0 1 1-8-8"/><path d="M20 4v8h-8"/></svg>', category: 'Misc Utility' },
  'layers': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>', category: 'Misc Utility' },
  'target': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M3 12h18"/><circle cx="12" cy="12" r="9"/></svg>', category: 'Misc Utility' },
  'quick-action': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>', category: 'Misc Utility' },
  'compass-guide': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M14.31 8l5.74 9.94M9.69 8h11.48M7.38 12l5.74-9.94M9.69 16L3.95 6.06M14.31 16H2.83M16.62 12l-5.74 9.94"/></svg>', category: 'Misc Utility' },
  'screen-display': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h20v14H2z"/><path d="M8 21h8M12 17v4"/></svg>', category: 'Misc Utility' },
  'protection': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>', category: 'Security' },
  'analytics-pulse': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h4l3-9 4 18 3-9h4"/></svg>', category: 'Charts & Data' },
  'global': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>', category: 'Communication' },
  'new-item': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8v8M8 12h8"/><circle cx="12" cy="12" r="10"/></svg>', category: 'Actions' },
  'card-badge': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>', category: 'Documents' },
  'verified-user': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M2 21l2-2M22 21l-2-2"/></svg>', category: 'HR / Employee Lifecycle' },
  'manual-guide': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>', category: 'Documents' },
  'tools': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>', category: 'Actions' },
  'customise': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/><path d="M2 2l20 20" stroke-width="0"/></svg>', category: 'Editing Actions' },
  'live-status': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/><circle cx="12" cy="12" r="1"/></svg>', category: 'Status & Future' },
  'options-menu': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M3 12h18M3 18h18"/><circle class="node" cx="20" cy="6" r="1.2" stroke="none"/><circle class="node" cx="4" cy="12" r="1.2" stroke="none"/><circle class="node" cx="20" cy="18" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'loading-spinner': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>', category: 'Status & Future' },
  'next-step': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/><circle class="node" cx="15" cy="12" r="1.2" stroke="none"/></svg>', category: 'Navigation' },
  'stamp-seal': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12l2.5 2.5L16 9"/><circle class="node" cx="19" cy="5" r="1.2" stroke="none"/></svg>', category: 'Legal & Compliance' },
  'certificate': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15a6 6 0 1 0 0-12 6 6 0 0 0 0 12z"/><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"/></svg>', category: 'Legal & Compliance' },
  'watermark': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4" stroke-dasharray="2 2"/><circle cx="12" cy="12" r="10" stroke-dasharray="2 2"/></svg>', category: 'Legal & Compliance' },
  'compliant-document': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 15l2 2 4-5"/></svg>', category: 'Legal & Compliance' },
  'legal-edit': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"/><path d="M16 8L2 22M17.5 15H9"/></svg>', category: 'Legal & Compliance' },
  'notarised': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4"/></svg>', category: 'Legal & Compliance' },
  'employee-id-card': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="9" cy="12" r="2"/><path d="M15 10h4M15 14h4M5 16c0-1.5 1.5-2.5 4-2.5s4 1 4 2.5"/></svg>', category: 'HR / Employee Lifecycle' },
  'onboarding': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 11l-3 3-2-2"/></svg>', category: 'HR / Employee Lifecycle' },
  'offboarding': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" y1="8" x2="22" y2="13"/><line x1="22" y1="8" x2="17" y2="13"/></svg>', category: 'HR / Employee Lifecycle' },
  'performance-review': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M12 3H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6"/><circle class="node" cx="4" cy="4" r="1.1" stroke="none"/></svg>', category: 'HR / Employee Lifecycle' },
  'payslip': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 9h20"/><path d="M6 13h4M6 16h6"/></svg>', category: 'HR / Employee Lifecycle' },
  'probation-period': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l3 2"/><path d="M12 2a10 10 0 0 1 0 20" stroke-dasharray="2 2"/></svg>', category: 'HR / Employee Lifecycle' },
  'deal-pipeline': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7.7 7.3L11 16M16.3 7.3L13 16"/></svg>', category: 'Client / CRM' },
  'meeting': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="M8 14h3v3H8z"/></svg>', category: 'Client / CRM' },
  'client-relationship': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/><path d="M20 8l1.5 1.5L18 13"/></svg>', category: 'Client / CRM' },
  'handoff': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M2 7h20l-2-5H4z"/><path d="M12 12V7"/></svg>', category: 'Client / CRM' },
  'follow-up': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 1 2.64 6.36L3 21"/><path d="M9 12h6M12 9v6"/></svg>', category: 'Client / CRM' },
  'page-setup': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="1" width="18" height="22" rx="1"/><rect x="6" y="4" width="12" height="16" rx="0.5" stroke-dasharray="2 1.5"/></svg>', category: 'Print & Export Settings' },
  'margins': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="1"/><rect x="6" y="6" width="12" height="12" stroke-dasharray="2 1.5"/></svg>', category: 'Print & Export Settings' },
  'paper-size-a4': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="1"/><text x="8" y="15" font-size="7" fill="currentColor" stroke="none">A4</text></svg>', category: 'Print & Export Settings' },
  'print-watermark': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" stroke-dasharray="3 2"/><text x="6" y="15" font-size="6" fill="currentColor" stroke="none">DRAFT</text></svg>', category: 'Print & Export Settings' },
  'export-as-pdf': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M12 18v-6M9.5 14.5L12 12l2.5 2.5"/></svg>', category: 'Print & Export Settings' },
  'comment': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-9 8.34 8.5 8.5 0 0 1-4.1-1.14L3 21l1.3-4.9A8.38 8.38 0 0 1 3.66 11.5 8.5 8.5 0 1 1 21 11.5z"/><circle class="node" cx="17" cy="6" r="1.1" stroke="none"/></svg>', category: 'Collaboration / Review' },
  'mention': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/><path d="M12 12a2 2 0 0 0 2-2" stroke-dasharray="1.5 1.5"/></svg>', category: 'Collaboration / Review' },
  'assign-to': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M17 11l2 2 4-4"/></svg>', category: 'Collaboration / Review' },
  'approve': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>', category: 'Collaboration / Review' },
  'reject': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>', category: 'Collaboration / Review' },
  'request-changes': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/><path d="M2 2l3 3" stroke-dasharray="1.5 1.5"/></svg>', category: 'Collaboration / Review' },
  'translate': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8h9M9 5v3M4 21l6-14 6 14M6.5 15h5"/><path d="M13 5c0 6 4 9 8 9"/></svg>', category: 'Language & Accessibility' },
  'font-size': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V4M20 20V4"/><text x="9" y="16" font-size="9" fill="currentColor" stroke="none">A</text></svg>', category: 'Language & Accessibility' },
  'high-contrast': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 0 20z"/></svg>', category: 'Language & Accessibility' },
  'screen-reader': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>', category: 'Language & Accessibility' },
  'api-webhook': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M10 6.5h4M17.5 10v4M14 17.5h-4M6.5 14v-4"/></svg>', category: 'Integration / Automation' },
  'connector-plugin': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M9 6h6a3 3 0 0 1 3 3v0M15 18H9a3 3 0 0 1-3-3v0"/></svg>', category: 'Integration / Automation' },
  'cloud-sync-drive': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22.5 12.5L13 2 4 12.5l4.5 8h9z"/><path d="M8.5 20.5L13 12l4.5 8.5"/></svg>', category: 'Integration / Automation' },
  'sync-2': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4.9 4.9a10 10 0 0 0 0 14.2M19.1 4.9a10 10 0 0 1 0 14.2"/><circle cx="12" cy="12" r="3"/><circle class="node" cx="19" cy="5" r="1.1" stroke="none"/></svg>', category: 'Integration / Automation' },
  'automation-workflow': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/><path d="M12 9v0" stroke-dasharray="0.5 0.5"/></svg>', category: 'Integration / Automation' },
  'keyboard-shortcut': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="6" height="4" rx="1"/><rect x="2" y="10" width="6" height="4" rx="1"/><rect x="2" y="16" width="6" height="4" rx="1"/><text x="10" y="8" font-size="6" fill="currentColor" stroke="none">K</text></svg>', category: 'Actions' },
  'spotlight-tooltip': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><path d="M12 3v2M12 19v2M21 12h-2M5 12H3"/></svg>', category: 'Misc Utility' },
  'version-compare': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h5"/><path d="M15 3h5a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-5"/><path d="M9 12h6"/></svg>', category: 'Misc Utility' },
  'backup-restore': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/><path d="M12 8v4l2.5 1.5"/></svg>', category: 'Data & Storage' },
  'rollback': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4v5h5"/><path d="M4.5 9a9 9 0 1 1 2 9.5"/><path d="M9 15l-4 3-1-5"/></svg>', category: 'Data & Storage' },
  'facebook': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>', category: 'Social' },
  'linkedin': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="9" width="4" height="12" rx="0.5"/><circle cx="4" cy="4" r="2"/><path d="M10 21v-8a2 2 0 0 1 4 0M10 13v0M14 13v8"/><path d="M14 13a4 4 0 0 1 8 0v8h-4v-8"/></svg>', category: 'Social' },
  'x-twitter': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4l16 16M20 4L4 20"/></svg>', category: 'Social' },
  'instagram': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4.5"/><circle cx="17.5" cy="6.5" r="1"/></svg>', category: 'Social' },
  'youtube': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22.5 8.5s-.2-1.6-.9-2.3c-.8-.9-1.7-.9-2.2-1C16.6 5 12 5 12 5h0s-4.6 0-7.4.2c-.5.1-1.4.1-2.2 1-.7.7-.9 2.3-.9 2.3S1.3 10.4 1.3 12.3v1.8c0 1.9.2 3.8.2 3.8s.2 1.6.9 2.3c.8.9 1.9.9 2.4 1 1.7.2 7.2.2 7.2.2s4.6 0 7.4-.2c.5-.1 1.4-.1 2.2-1 .7-.7.9-2.3.9-2.3s.2-1.9.2-3.8v-1.8c0-1.9-.2-3.8-.2-3.8z"/><path d="M9.8 15.5l6-3.2-6-3.2z"/></svg>', category: 'Social' },
  'desk': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20h20M4 20V8h16v12M4 8l2-4h12l2 4"/><path d="M9 12h6"/></svg>', category: 'Office / Workspace' },
  'chair': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 19v-6a6 6 0 0 1 12 0v6"/><path d="M4 19h16v2H4zM6 13h12"/></svg>', category: 'Office / Workspace' },
  'meeting-room': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M2 10h20M7 6V4M17 6V4"/></svg>', category: 'Office / Workspace' },
  'whiteboard': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="14" rx="1"/><path d="M8 22h8M12 18v4M6 9h5M6 13h8"/></svg>', category: 'Office / Workspace' },
  'filing-cabinet': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="1"/><path d="M4 9h16M4 15h16M9 9v6M15 9v6"/></svg>', category: 'Office / Workspace' },
  'coffee-break': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>', category: 'Office / Workspace' },
  'conference-table': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="12" rx="9" ry="5"/><path d="M3 12v4a9 5 0 0 0 18 0v-4"/></svg>', category: 'Office / Workspace' },
  'office-plant': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8 2 6 5 6 9c0 6 3 9 3 13M9 9a3 3 0 0 1 6 0M6 22h12"/></svg>', category: 'Office / Workspace' },
  'stapler': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12l16-8v6l-16 8z"/><path d="M4 18h6"/></svg>', category: 'Office / Workspace' },
  'scissors': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.5 15.5M14.5 14.5L20 20M8.5 8.5L12 12"/></svg>', category: 'Office / Workspace' },
  'pen': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>', category: 'Office / Workspace' },
  'pencil': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>', category: 'Office / Workspace' },
  'notebook': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h13l3 3v13H4z"/><path d="M8 9h8M8 13h8M8 17h5"/><path d="M4 8h4"/></svg>', category: 'Office / Workspace' },
  'sticky-note': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h13v13l-3 3H4z"/><path d="M17 17h-3v3"/></svg>', category: 'Office / Workspace' },
  'desk-phone': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="9" width="16" height="12" rx="1"/><path d="M8 9V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v3"/><circle cx="12" cy="15" r="2"/></svg>', category: 'Office / Workspace' },
  'fax-machine': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="10" rx="1"/><path d="M7 18h10M12 14v4"/><rect x="6" y="7" width="12" height="4"/></svg>', category: 'Office / Workspace' },
  'scanner': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="10" rx="1"/><path d="M3 11h18M8 4h8v3H8z"/></svg>', category: 'Office / Workspace' },
  'photocopier': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="8" width="20" height="9" rx="1"/><path d="M6 8V4h12v4M6 21l1-4h10l1 4"/></svg>', category: 'Office / Workspace' },
  'projector': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8a2 2 0 0 1 2-2h4l2-2h2l2 2h4a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><circle cx="12" cy="12" r="3"/></svg>', category: 'Office / Workspace' },
  'monitor': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="1"/><path d="M8 20h8M12 16v4"/></svg>', category: 'Office / Workspace' },
  'keyboard': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h12"/></svg>', category: 'Office / Workspace' },
  'mouse': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a6 6 0 0 1 6 6v6a6 6 0 0 1-12 0V8a6 6 0 0 1 6-6z"/><path d="M12 2v6"/></svg>', category: 'Office / Workspace' },
  'headset': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 14v-2a9 9 0 0 1 18 0v2"/><rect x="1" y="14" width="6" height="7" rx="2"/><rect x="17" y="14" width="6" height="7" rx="2"/></svg>', category: 'Office / Workspace' },
  'water-cooler': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2h8l2 6H6z"/><path d="M6 8h12v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1z"/><path d="M9 14h6"/></svg>', category: 'Office / Workspace' },
  'trash-bin': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/><path d="M10 11v6M14 11v6"/></svg>', category: 'Office / Workspace' },
  'bookshelf': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18M8 3v18M14 3v18"/></svg>', category: 'Office / Workspace' },
  'wall-clock': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/><circle class="node" cx="12" cy="3" r="1" stroke="none"/></svg>', category: 'Office / Workspace' },
  'door': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="1"/><path d="M15 12h.01"/></svg>', category: 'Office / Workspace' },
  'window': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 12h18M12 4v16"/></svg>', category: 'Office / Workspace' },
  'elevator': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="1"/><path d="M10 8l2-2 2 2M10 16l2 2 2-2"/></svg>', category: 'Office / Workspace' },
  'parking': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 8h3.5a2.5 2.5 0 0 1 0 5H9V8zM9 13v5"/></svg>', category: 'Office / Workspace' },
  'reception': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21V10l9-6 9 6v11"/><path d="M9 21v-6h6v6M3 10h18"/></svg>', category: 'Office / Workspace' },
  'cubicle-layout': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="9" height="9" rx="1"/><rect x="13" y="2" width="9" height="9" rx="1"/><rect x="2" y="13" width="9" height="9" rx="1"/><rect x="13" y="13" width="9" height="9" rx="1"/></svg>', category: 'Office / Workspace' },
  'standing-desk': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M20 20V10M4 10l8-6 8 6"/><path d="M9 20v-6h6v6"/></svg>', category: 'Office / Workspace' },
  'desk-lamp': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2h6M12 2v6M6 20h12M8 20l4-12 4 12"/></svg>', category: 'Office / Workspace' },
  'power-outlet': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="4" width="8" height="16" rx="2"/><circle cx="10.5" cy="9" r="0.6" fill="currentColor" stroke="none"/><circle cx="13.5" cy="9" r="0.6" fill="currentColor" stroke="none"/></svg>', category: 'Office / Workspace' },
  'extension-cord': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h4l2 4-2 4h-4M20 6h-4l-2 4 2 4h4"/><path d="M10 10h4"/></svg>', category: 'Office / Workspace' },
  'marker-pen': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>', category: 'Office / Workspace' },
  'corkboard': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="1"/><circle cx="7" cy="7" r="1"/><circle cx="14" cy="6" r="1"/><circle cx="18" cy="12" r="1"/><circle cx="8" cy="16" r="1"/></svg>', category: 'Office / Workspace' },
  'door-sign': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="10" rx="1"/><path d="M7 11h10M7 14h6"/></svg>', category: 'Office / Workspace' },
  'locker': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="1"/><circle cx="12" cy="12" r="1"/><path d="M4 8h16"/></svg>', category: 'Office / Workspace' },
  'storage-box': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8L12 3 3 8l9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/></svg>', category: 'Office / Workspace' },
  'recycling-bin': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10l5-6 5 6M7 10v10a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V10M7 10H5m14 0h2"/></svg>', category: 'Office / Workspace' },
  'air-conditioner': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="8" rx="1"/><path d="M6 14v3M12 14v5M18 14v3"/></svg>', category: 'Office / Workspace' },
  'fire-extinguisher': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2h4v3h-4z"/><path d="M9 5h6l1 4H8z"/><path d="M8 9h8l-1 12H9z"/></svg>', category: 'Office / Workspace' },
  'first-aid-kit': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="14" rx="1"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/><path d="M12 11v5M9.5 13.5h5"/></svg>', category: 'Office / Workspace' },
  'security-camera': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="3"/></svg>', category: 'Office / Workspace' },
  'access-card': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="12" cy="10" r="3"/><path d="M8 21v-3a4 4 0 0 1 8 0v3"/></svg>', category: 'Office / Workspace' },
  'wifi-router': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5a11 11 0 0 1 14 0M8.5 16a6 6 0 0 1 7 0M12 19.5h.01"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>', category: 'Office / Workspace' },
  'server-rack': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="8" rx="1"/><rect x="4" y="14" width="16" height="8" rx="1"/><circle cx="8" cy="6" r="0.8" fill="currentColor" stroke="none"/><circle cx="8" cy="18" r="0.8" fill="currentColor" stroke="none"/></svg>', category: 'Office / Workspace' },
  'phone-basic': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3C3 13.4 10.6 21 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4-2 2a15 15 0 0 1-5.4-5.4l2-2z"/></svg>', category: 'Contact' },
  'mobile-phone': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>', category: 'Contact' },
  'desk-phone-2': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="9" width="16" height="12" rx="1"/><path d="M8 9V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v3"/><circle cx="12" cy="15" r="2"/></svg>', category: 'Contact' },
  'call-forward': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M16 2l6 6-6 6M22 8H10a4 4 0 0 0-4 4v10"/></svg>', category: 'Contact' },
  'incoming-call': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-3-3-3 3M20 4v9a4 4 0 0 1-4 4H4"/></svg>', category: 'Contact' },
  'outgoing-call': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2l3 3-3 3M20 5H8a4 4 0 0 0-4 4v9"/></svg>', category: 'Contact' },
  'missed-call': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L2 22"/><path d="M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3c0 3 .8 5.9 2.2 8.4M14.5 17.8A17 17 0 0 0 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4"/></svg>', category: 'Contact' },
  'phone-off-silent': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M1 1l22 22"/><path d="M14.5 8.5a3.5 3.5 0 0 1 1 2.5M18 6a7 7 0 0 1 2 5M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3C3 13.4 10.6 21 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4-2 2"/></svg>', category: 'Contact' },
  'ringing': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M8.2 3.5H4.8A1.8 1.8 0 0 0 3 5.3C3 13.4 10.6 21 18.7 21a1.8 1.8 0 0 0 1.8-1.8v-3.4l-4.2-1.4-2 2a15 15 0 0 1-5.4-5.4l2-2z"/><path d="M15 2a5 5 0 0 1 5 5M15 5a2 2 0 0 1 2 2"/></svg>', category: 'Contact' },
  'voicemail': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><circle cx="12" cy="11" r="3"/><path d="M8 21h8"/></svg>', category: 'Contact' },
  'call-contact': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/><path d="M20 8v4M22 10h-4"/></svg>', category: 'Contact' },
  'video-call-2': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>', category: 'Contact' },
  'contact-support': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8.2 8.5H6.8A.9.9 0 0 0 6 9.4c0 4 3.8 7.6 7.8 7.6a.9.9 0 0 0 .9-.9v-1.7l-2.1-.7-1 1a7.6 7.6 0 0 1-2.7-2.7l1-1-.7-2.1z"/></svg>', category: 'Contact' },
  'landline-booth': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8 2 6 5 6 9c0 6 3 9 3 13h6c0-4 3-7 3-13 0-4-2-7-6-7z"/><path d="M8.5 9h7"/></svg>', category: 'Contact' },
  'conference-phone': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M8 14h8"/></svg>', category: 'Contact' },
  'remote-work-laptop': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="14" rx="1"/><path d="M2 18h20l-2 3H4z"/><path d="M8 10l2 2-2 2M13 14h3"/></svg>', category: 'Remote Work' },
  'video-meeting': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>', category: 'Remote Work' },
  'timezone': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9M21 12a9 9 0 0 1-9 9"/><circle cx="3" cy="12" r="1.5"/><circle cx="21" cy="12" r="1.5"/><path d="M12 3v3M12 18v3"/></svg>', category: 'Remote Work' },
  'wifi-connectivity': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5a11 11 0 0 1 14 0M8.5 16a6 6 0 0 1 7 0M12 19.5h.01"/></svg>', category: 'Remote Work' },
  'headset-support': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 14v-2a9 9 0 0 1 18 0v2"/><rect x="1" y="14" width="6" height="7" rx="2"/><rect x="17" y="14" width="6" height="7" rx="2"/></svg>', category: 'Remote Work' },
  'home-office': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V10l9-6 9 6v11"/><path d="M9 21v-6h6v6"/><circle class="node" cx="20" cy="5" r="1.1" stroke="none"/></svg>', category: 'Remote Work' },
  'virtual-desk': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M8 10h8M8 14h5"/><circle class="node" cx="20" cy="4" r="1.1" stroke="none"/></svg>', category: 'Remote Work' },
  'global-team': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20z"/></svg>', category: 'Remote Work' },
  'async-collaboration': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="4"/><path d="M3 21v-2a6 6 0 0 1 12 0v2"/><path d="M17 8l2 2 4-4"/></svg>', category: 'Remote Work' },
  'task-complete-remote': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/><path d="M9 9l2 2 4-4"/></svg>', category: 'Remote Work' },
  'flexible-hours': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/><circle class="node" cx="19" cy="5" r="1" stroke="none"/></svg>', category: 'Remote Work' },
  'freelancer': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M2 4l20 16" stroke-dasharray="2 2"/></svg>', category: 'Remote Work' },
  'secure-remote-access': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V8a5 5 0 0 1 10 0v3"/></svg>', category: 'Remote Work' },
  'cross-border-hiring': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M2 12h20M12 2c2.5 2.5 4 6 4 10s-1.5 7.5-4 10c-2.5-2.5-4-6-4-10s1.5-7.5 4-10z"/></svg>', category: 'Remote Work' },
  'employee-directory': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><path d="M15 9h2M15 13h2M9 17h8"/></svg>', category: 'Remote Work' },
  'productivity': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>', category: 'Remote Work' },
  'coworking-hub': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M2 12h20"/><circle cx="12" cy="12" r="9"/></svg>', category: 'Remote Work' },
  'onboarding-portal': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="8" cy="12" r="2"/><path d="M14 9h4M14 12h4M14 15h2"/></svg>', category: 'Remote Work' },
  'hire-remote': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/></svg>', category: 'Remote Work' },
  '247-availability': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/><path d="M2 12h2M20 12h2M12 2v2M12 20v2"/></svg>', category: 'Remote Work' },
  'org-chart': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><path d="M12 8v5M12 13l-7 3M12 13l7 3"/></svg>', category: 'Organisation' },
  'departments': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>', category: 'Organisation' },
  'branch-office': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M6 21V7l6-4 6 4v14"/><path d="M10 9h.01M14 9h.01M10 13h.01M14 13h.01"/></svg>', category: 'Organisation' },
  'team-group': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>', category: 'Organisation' },
  'leadership': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/><path d="M12 3v2M12 3a5 5 0 0 1 5 5"/></svg>', category: 'Organisation' },
  'merger': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M9 6h6"/><path d="M6 9v6M18 9v6"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><path d="M9 18h6"/></svg>', category: 'Organisation' },
  'restructure': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12a10 10 0 1 1 5 8.7"/><path d="M2 12v6h6"/></svg>', category: 'Organisation' },
  'growth-strategy': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg>', category: 'Organisation' },
  'headquarters': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V10l9-6 9 6v11"/><path d="M9 21v-6h6v6"/><path d="M4 10h18"/><circle class="node" cx="20" cy="5" r="1.1" stroke="none"/></svg>', category: 'Organisation' },
  'company-profile': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M2 12h20M12 7V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v2"/></svg>', category: 'Organisation' },
  'policy-document': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"/><path d="M16 8L2 22M17.5 15H9"/></svg>', category: 'Organisation' },
  'governance': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6a6 6 0 0 0-6 6M12 6a6 6 0 0 1 6 6"/><circle cx="12" cy="12" r="2"/></svg>', category: 'Organisation' },
  'compliance-status': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>', category: 'Organisation' },
  'risk-management': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 3v6c0 5-3.5 8.5-8 11-4.5-2.5-8-6-8-11V5z"/><path d="M9 12l2 2 4-4"/></svg>', category: 'Organisation' },
  'org-calendar': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 9h20M8 4v5M16 4v5"/></svg>', category: 'Organisation' },
  'corporate-building': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V10l9-6 9 6v11"/><path d="M9 21v-9h6v9"/><path d="M4 10h18"/><path d="M9 6h6"/></svg>', category: 'Organisation' },
  'cross-functional': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18M8 8l8 8M16 8l-8 8"/></svg>', category: 'Organisation' },
  'business-unit': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6l2 4h12v12H2z"/><path d="M12 12h6"/></svg>', category: 'Organisation' },
  'internal-comms': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>', category: 'Organisation' },
  'kpi-performance': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 8l-5 5-3-3-4 4"/></svg>', category: 'Organisation' },
  'market-share': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 10 10h-10z"/></svg>', category: 'Organisation' },
  'corporate-governance': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>', category: 'Organisation' },
  'board-meeting': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><circle cx="7" cy="6" r="1"/><circle cx="10" cy="6" r="1"/></svg>', category: 'Organisation' },
  'delegation': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M12 14h5l3 3-3 3h-5"/></svg>', category: 'Organisation' },
  'mission-accomplished': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/><circle class="node" cx="19" cy="5" r="1" stroke="none"/></svg>', category: 'Organisation' },
  'share-2': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.6M8.2 13.2l7.6 4.6"/></svg>', category: 'Social' },
  'network': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M6.5 6.5L10.5 10.5M17.5 6.5L13.5 10.5M6.5 17.5L10.5 13.5M17.5 17.5L13.5 13.5"/></svg>', category: 'Social' },
  'connect': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="12" r="3"/><circle cx="17" cy="12" r="3"/><path d="M10 12h4"/></svg>', category: 'Social' },
  'broadcast': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4.9 19.1a10 10 0 1 1 14.2 0"/><path d="M8 16a5 5 0 1 1 8 0"/><circle cx="12" cy="12" r="1.5"/></svg>', category: 'Social' },
  'community': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="3"/><circle cx="17" cy="7" r="3"/><circle cx="9" cy="17" r="3"/><circle cx="17" cy="17" r="3"/><path d="M9 10v4M17 10v4M12 7h2M12 17h2"/></svg>', category: 'Social' },
  'follow': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="8.5" cy="8.5" r="4"/><path d="M2 20a6.5 6.5 0 0 1 13 0"/><path d="M17 8l2 2 4-4"/></svg>', category: 'Social' },
  'unfollow': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="8.5" cy="8.5" r="4"/><path d="M2 20a6.5 6.5 0 0 1 13 0"/><line x1="17" y1="8" x2="23" y2="8"/></svg>', category: 'Social' },
  'public-post': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12h8M12 8v8"/></svg>', category: 'Social' },
  'private-post': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>', category: 'Social' },
  'reaction-engagement': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.8 1-1a5.5 5.5 0 0 0 0-7.6z"/><path d="M9 12h6M12 9v6" stroke-dasharray="1.5 1.5"/></svg>', category: 'Social' },
  'comment-thread': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M7 9h10M7 13h6"/></svg>', category: 'Social' },
  'repost': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 1l4 4-4 4M3 11V9a4 4 0 0 1 4-4h14M7 23l-4-4 4-4M21 13v2a4 4 0 0 1-4 4H3"/><circle class="node" cx="12" cy="12" r="1.2" stroke="none"/></svg>', category: 'Social' },
  'live-stream': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2"/><path d="M12 2a10 10 0 0 1 10 10M12 2a10 10 0 0 0-10 10M2 12a10 10 0 0 0 10 10M22 12a10 10 0 0 1-10 10" stroke-dasharray="3 2"/></svg>', category: 'Social' },
  'audience-reach': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/><path d="M14 14l3 3 5-5"/></svg>', category: 'Social' },
  'trending': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/><circle class="node" cx="8.5" cy="10.5" r="1.1" stroke="none"/></svg>', category: 'Social' },
  'hashtag': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="9" x2="19" y2="9"/><line x1="5" y1="15" x2="19" y2="15"/><line x1="9" y1="4" x2="7" y2="20"/><line x1="17" y1="4" x2="15" y2="20"/></svg>', category: 'Social' },
  'mention-2': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/><path d="M15 5l2 2 3-3" stroke-dasharray="1 1"/></svg>', category: 'Social' },
  'group-circle': { svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="8" r="3"/><circle cx="17" cy="8" r="3"/><circle cx="12" cy="16" r="3"/><path d="M9 10l2 4M15 10l-2 4"/></svg>', category: 'Social' }
};

const CATEGORIES = Object.values(ICON_LIBRARY).reduce((acc, i) => {
  acc[i.category] = (acc[i.category] || 0) + 1;
  return acc;
}, {});

let ipTargetElement = null; // the .icon span currently being edited
let ipSelectedKey = null;

function openIconPicker(targetIconElement){
  ipTargetElement = targetIconElement;
  ipSelectedKey = null;
  document.getElementById('iconPickerOverlay').classList.add('open');
  renderIconPickerCategories();
  renderIconPickerGrid('all', '');
  document.getElementById('ipSearchInput').value = '';
  document.getElementById('ipSearchInput').focus();
}

function closeIconPicker(){
  document.getElementById('iconPickerOverlay').classList.remove('open');
  ipTargetElement = null;
}

function renderIconPickerCategories(){
  const listEl = document.getElementById('ipCatList');
  listEl.innerHTML = '';
  document.getElementById('ipCountAll').textContent = Object.keys(ICON_LIBRARY).length;
  Object.keys(CATEGORIES).sort().forEach(cat => {
    const div = document.createElement('div');
    div.className = 'ip-cat';
    div.dataset.cat = cat;
    div.textContent = `${cat} `;
    const span = document.createElement('span');
    span.textContent = CATEGORIES[cat];
    div.appendChild(span);
    div.onclick = () => {
      document.querySelectorAll('.ip-cat').forEach(c => c.classList.remove('on'));
      div.classList.add('on');
      renderIconPickerGrid(cat, document.getElementById('ipSearchInput').value);
    };
    listEl.appendChild(div);
  });
  document.querySelector('.ip-cat[data-cat="all"]').onclick = () => {
    document.querySelectorAll('.ip-cat').forEach(c => c.classList.remove('on'));
    document.querySelector('.ip-cat[data-cat="all"]').classList.add('on');
    renderIconPickerGrid('all', document.getElementById('ipSearchInput').value);
  };
}

function renderIconPickerGrid(category, searchTerm){
  const grid = document.getElementById('ipGrid');
  grid.innerHTML = '';
  const term = searchTerm.trim().toLowerCase();
  Object.entries(ICON_LIBRARY).forEach(([key, icon]) => {
    if(category !== 'all' && icon.category !== category) return;
    if(term && !key.replace(/-/g,' ').includes(term)) return;
    const cell = document.createElement('div');
    cell.className = 'ip-gi' + (key === ipSelectedKey ? ' sel' : '');
    cell.innerHTML = icon.svg;
    cell.title = key.replace(/-/g,' ');
    cell.onclick = () => {
      ipSelectedKey = key;
      document.querySelectorAll('.ip-gi').forEach(g => g.classList.remove('sel'));
      cell.classList.add('sel');
    };
    cell.ondblclick = () => { ipSelectedKey = key; applyIconSelection(); };
    grid.appendChild(cell);
  });
}

document.getElementById('ipSearchInput').addEventListener('input', (e) => {
  const activeCat = document.querySelector('.ip-cat.on')?.dataset.cat || 'all';
  renderIconPickerGrid(activeCat, e.target.value);
});

function applyIconSelection(){
  if(!ipTargetElement || !ipSelectedKey) return;
  ipTargetElement.innerHTML = ICON_LIBRARY[ipSelectedKey].svg;
  closeIconPicker();
  dzRefreshIconGrid();
}

document.getElementById('iconPickerOverlay').addEventListener('click', function(e){
  if(e.target.id === 'iconPickerOverlay') closeIconPicker();
});

/* ── Design Customizer: Icons section ── */
function dzRefreshIconGrid(){
  var hGrid = document.getElementById('dzHeaderIcons');
  var fGrid = document.getElementById('dzFooterIcons');
  if(!hGrid || !fGrid) return;
  hGrid.innerHTML = '';
  fGrid.innerHTML = '';
  var headerIcons = document.querySelectorAll('.brand-details > div:not(.add-header-line) > .icon');
  headerIcons.forEach(function(iconEl){
    var thumb = document.createElement('div');
    thumb.className = 'dz-icon-thumb';
    thumb.innerHTML = iconEl.innerHTML;
    thumb.addEventListener('click', function(){ openIconPicker(iconEl); });
    hGrid.appendChild(thumb);
  });
  var footerIcons = document.querySelectorAll('.footer .footer-icon');
  footerIcons.forEach(function(iconEl){
    var thumb = document.createElement('div');
    thumb.className = 'dz-icon-thumb';
    thumb.innerHTML = iconEl.innerHTML;
    thumb.addEventListener('click', function(){ openIconPicker(iconEl); });
    fGrid.appendChild(thumb);
  });
}
dzRefreshIconGrid();

// ---- Template Customize full-screen mode ----
(function(){
  var tcBtn = document.getElementById('templateCustomizeBtn');
  var tcMode = document.getElementById('templateCustomizeMode');
  var tcExit = document.getElementById('tcExitBtn');
  var tcApply = document.getElementById('tcApplyBtn');
  var tcHide = document.getElementById('tcHidePanelBtn');
  var tcPanel = document.getElementById('tcPanel');
  var tcCollapse = document.getElementById('tcCollapseBtn');
  var tcPreview = document.getElementById('tcPreviewArea');
  // Multi-page documents (e.g. Agreement Letter's 2 pages) have more than
  // one .page under .app-bodyarea - move every one of them into the
  // preview together, not just the first.
  var pages = document.querySelectorAll('.app-bodyarea .page');
  var appBodyArea = document.querySelector('.app-bodyarea');
  if(!tcBtn || !tcMode || !pages.length) return;

  function tcOpen(){
    pages.forEach(function(p){ tcPreview.appendChild(p); });
    tcMode.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function tcClose(){
    pages.forEach(function(p){ appBodyArea.appendChild(p); });
    tcMode.classList.remove('open');
    document.body.style.overflow = '';
  }
  tcBtn.addEventListener('click', tcOpen);
  tcExit.addEventListener('click', tcClose);
  tcApply.addEventListener('click', tcClose);

  tcHide.addEventListener('click', function(){
    var isCollapsed = tcPanel.classList.contains('collapsed');
    if(isCollapsed){
      tcPanel.classList.remove('collapsed');
      tcHide.textContent = 'Hide Panel';
    } else {
      tcPanel.classList.add('collapsed');
      tcHide.textContent = 'Show Panel';
    }
  });

  tcCollapse.addEventListener('click', function(){
    tcPanel.classList.toggle('collapsed');
    tcHide.textContent = tcPanel.classList.contains('collapsed') ? 'Show Panel' : 'Hide Panel';
  });

  var tcSecs = tcPanel.querySelectorAll('.tc-sec');
  tcSecs.forEach(function(sec){
    sec.addEventListener('click', function(){
      tcSecs.forEach(function(s){ s.classList.remove('on'); });
      sec.classList.add('on');
      var target = sec.getAttribute('data-tc-sec');
      var dzSec = document.getElementById('dz-' + target);
      if(dzSec){
        document.querySelectorAll('.dz-section').forEach(function(s){ s.classList.remove('open'); });
        dzSec.classList.add('open');
      }
    });
  });
})();
