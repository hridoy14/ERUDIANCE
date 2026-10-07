// ---- Shared sidebar: single source of truth for every page ----
// Every page (Offer Letter, Invoice, Employee Invoice, and any future page)
// renders the exact same sidebar from this one file instead of keeping a
// copy-pasted <nav> block in each HTML file. Edit the markup here once and
// every page picks it up on next load.
//
// A page just needs an empty mount point:
//   <nav class="app-sidebar" id="appSidebar"></nav>
// This script fills it in, then highlights whichever item matches the
// current page (or whichever one was actually clicked, when more than one
// item points at the same page - e.g. "Client Invoice"/"Employee Invoice").

var SIDEBAR_LOGO = 'data:image/png;base64,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';

var SIDEBAR_ITEMS = [
  { type: 'label', text: 'WORKER' },
  { type: 'link', navId: 'offer-letter', href: 'erudience_offer_letter.html',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 4h16v16H4z"/><path d="M4 9h16M9 4v16"/></svg>',
    label: 'Offer Letter' },
  { type: 'link', navId: 'agreement-letter', href: 'agreement-letter.html',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/></svg>',
    label: 'Agreement Letter' },
  { type: 'disabled',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/></svg>',
    label: 'Termination Letter', soon: true },

  { type: 'label', text: 'CLIENT' },
  { type: 'link', navId: 'client-proposal', href: 'client-proposal.html',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 4h16v16H4z"/><path d="M8 9h8M8 13h5"/></svg>',
    label: 'Client Proposal' },
  { type: 'disabled',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/></svg>',
    label: 'Showcase Letter', soon: true },

  { type: 'label', text: 'INVOICE' },
  { type: 'link', navId: 'client-invoice', href: 'invoice.html', subitem: true,
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h8"/></svg>',
    label: 'Client Invoice' },
  { type: 'link', navId: 'employee-invoice', href: 'employee-invoice.html', subitem: true,
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6"/><circle cx="9.5" cy="13" r=".3"/></svg>',
    label: 'Employee Invoice' },

  { type: 'label', text: 'CUSTOMIZER' },
  { type: 'button', id: 'templateCustomizeBtn',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/><circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.9 0 1.6-.7 1.6-1.7 0-.4-.2-.8-.4-1.1-.3-.3-.4-.7-.4-1.1a1.6 1.6 0 0 1 1.7-1.7h2c3 0 5.5-2.5 5.5-5.5C22 6 17.5 2 12 2z"/></svg>',
    label: 'Template Customize' }
];

// Pages that don't load app.js (e.g. a form wizard with no document to
// style) don't get a working Template Customize button - show it visually
// disabled there instead of a dead click.
var NO_TEMPLATE_CUSTOMIZE = { 'client-proposal.html': true };

function renderSidebarHTML(pageFile){
  var html = '<div class="sb-brand"><img src="' + SIDEBAR_LOGO + '" alt="Erudience"><span>ERUDIENCE</span></div>';

  SIDEBAR_ITEMS.forEach(function(item){
    if(item.type === 'label'){
      html += '<div class="sb-grouplabel">' + item.text + '</div>';
    } else if(item.type === 'link'){
      html += '<a class="sb-item' + (item.subitem ? ' sb-subitem' : '') + '" href="' + item.href + '" data-nav-id="' + item.navId + '">' +
        item.icon + '\n      ' + item.label + '\n    </a>';
    } else if(item.type === 'disabled'){
      html += '<div class="sb-item disabled' + (item.subitem ? ' sb-subitem' : '') + '">' +
        item.icon + '\n      ' + item.label + (item.soon ? ' <span class="sb-soon">Soon</span>' : '') + '\n    </div>';
    } else if(item.type === 'button'){
      if(item.id === 'templateCustomizeBtn' && NO_TEMPLATE_CUSTOMIZE[pageFile]){
        html += '<div class="sb-item disabled">' + item.icon + '\n      ' + item.label + '\n    </div>';
      } else {
        html += '<button class="sb-item" id="' + item.id + '" type="button">' +
          item.icon + '\n      ' + item.label + '\n    </button>';
      }
    }
  });

  return html;
}

// ---- Shared top toolbar: title + Print/Save as PDF + Reset ----
// Same idea as the sidebar - one definition, every page just needs an empty
// mount point: <div class="app-toolbar" id="appToolbar"></div>
// The title shown is picked from this map by the current page's filename;
// add an entry here when a new document page is connected.
var TOOLBAR_TITLES = {
  'erudience_offer_letter.html': 'Offer of Employment',
  'invoice.html': 'Invoice',
  'employee-invoice.html': 'Employee Invoice',
  'agreement-letter.html': 'Agreement Letter',
  'client-proposal.html': 'Client Proposal'
};

// Pages without app.js's per-page Reset (e.g. a multi-step wizard with its
// own Save/Load/Download/Upload Draft system) don't get a "Reset Letter"
// button in the shared toolbar - it would have nothing to wire up to.
var TOOLBAR_NO_RESET = { 'client-proposal.html': true };

function renderToolbarHTML(pageFile){
  var title = TOOLBAR_TITLES[pageFile] || document.title || 'Document';
  var html = '<div class="app-doctitle">' + title + '</div>' +
    '<button class="btn-print" id="btnPrintDoc" type="button">Print / Save as PDF</button>';
  if(!TOOLBAR_NO_RESET[pageFile]){
    html += '<button class="btn-reset" id="resetLetterBtn" type="button">Reset Letter</button>';
  }
  return html;
}

(function(){
  var mount = document.getElementById('appToolbar');
  if(!mount) return;
  var current = location.pathname.split('/').pop() || 'erudience_offer_letter.html';
  mount.innerHTML = renderToolbarHTML(current);

  var printBtn = document.getElementById('btnPrintDoc');
  if(printBtn){
    printBtn.addEventListener('click', function(){
      // printCurrent()/printOfferLetter() are defined by the page's own
      // script / app.js, loaded right after this one - by the time a user
      // can actually click, whichever applies is ready.
      if(typeof printCurrent === 'function') printCurrent();
      else if(typeof printOfferLetter === 'function') printOfferLetter();
      else window.print();
    });
  }
})();

// ---- Mount + active-state highlight ----
// Several sidebar items can point to the same page (e.g. "Client Invoice"
// and "Employee Invoice" are distinct pages now, but earlier revisions had
// overlapping hrefs) so matching by href alone would light up every item
// that shares that page. We remember which specific item was clicked (by
// its data-nav-id) and restore that single highlight on load.
(function(){
  var mount = document.getElementById('appSidebar');
  if(!mount) return;
  var currentPage = location.pathname.split('/').pop() || 'erudience_offer_letter.html';
  mount.innerHTML = renderSidebarHTML(currentPage);

  var STORAGE_KEY = 'erudienceActiveNavId';
  var current = currentPage;

  var navLinks = mount.querySelectorAll('.sb-item[href][data-nav-id]');

  navLinks.forEach(function(el){
    el.addEventListener('click', function(){
      try{ sessionStorage.setItem(STORAGE_KEY, el.getAttribute('data-nav-id')); }catch(e){}
    });
  });

  var storedId = null;
  try{ storedId = sessionStorage.getItem(STORAGE_KEY); }catch(e){}

  var toActivate = null;

  if(storedId){
    var stored = mount.querySelector('.sb-item[data-nav-id="' + storedId + '"]');
    if(stored && stored.getAttribute('href') === current){
      toActivate = stored;
    }
  }

  if(!toActivate){
    // Fallback (direct URL load, back/forward, or first visit): prefer a
    // non-subitem link matching the current page, else the first link that
    // matches at all.
    navLinks.forEach(function(el){
      if(!toActivate && el.getAttribute('href') === current && !el.classList.contains('sb-subitem')){
        toActivate = el;
      }
    });
    if(!toActivate){
      navLinks.forEach(function(el){
        if(!toActivate && el.getAttribute('href') === current){
          toActivate = el;
        }
      });
    }
  }

  navLinks.forEach(function(el){
    if(el === toActivate){
      el.classList.add('active');
      try{ sessionStorage.setItem(STORAGE_KEY, el.getAttribute('data-nav-id')); }catch(e){}
    } else {
      el.classList.remove('active');
    }
  });
})();
