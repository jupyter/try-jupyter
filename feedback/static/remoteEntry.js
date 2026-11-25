// A prebuilt JupyterLab extension written by hand, so the site needs no build step:
// it uses the application object, the page, and the translator from the shared packages.
(function () {
  'use strict';

  const NAME = 'try-jupyter-feedback';
  const COMMAND = 'try-jupyter:report-problem';

  // Keep in step with KERNELS_TO_KEEP in scripts/filter_xeus_kernels.py.
  const XEUS_KERNELS = new Set([
    'xpython',
    'xcpp23',
    'xc23',
    'xr',
    'xsqlite',
    'fortran'
  ]);

  // Language packs only cover published extensions, so this one carries its own translations.
  // Each header copies the language code and plural rule of the matching language pack.
  const TRANSLATIONS = {
    'fr-FR': {
      '': { language: 'fr-FR', pluralForms: 'nplurals=2; plural=(n > 1);' },
      'Report a Problem…': ['Signaler un problème…'],
      'Report a Problem': ['Signaler un problème'],
      'What is the problem about?': ['Sur quoi porte le problème ?'],
      'The Jupyter Notebook interface: menus, editing, layout': [
        "L'interface de Jupyter Notebook : menus, édition, mise en page"
      ],
      'The JupyterLab interface: menus, editing, layout': [
        "L'interface de JupyterLab : menus, édition, mise en page"
      ],
      'Running code in the %1 kernel': ["L'exécution de code dans le noyau %1"],
      'Running code': ["L'exécution de code"],
      'Opening, saving or uploading files': [
        "L'ouverture, l'enregistrement ou le téléversement de fichiers"
      ],
      'The terminal': ['Le terminal'],
      'The AI assistant': ["L'assistant IA"],
      'An example notebook, or I am not sure': [
        "Un notebook d'exemple, ou je ne sais pas"
      ],
      'This opens a new GitHub issue with the details of this page filled in, and copies the details to the clipboard. You need a GitHub account to submit the issue.':
        [
          "Cela ouvre un nouveau ticket GitHub prérempli avec les détails de cette page, et copie ces détails dans le presse-papiers. Vous avez besoin d'un compte GitHub pour soumettre le ticket."
        ],
      Cancel: ['Annuler'],
      'Continue on GitHub': ['Continuer sur GitHub']
    },
    'zh-CN': {
      '': { language: 'zh-CN', pluralForms: 'nplurals=1; plural=0;' },
      'Report a Problem…': ['报告问题…'],
      'Report a Problem': ['报告问题'],
      'What is the problem about?': ['问题与哪方面有关？'],
      'The Jupyter Notebook interface: menus, editing, layout': [
        'Jupyter Notebook 界面：菜单、编辑、布局'
      ],
      'The JupyterLab interface: menus, editing, layout': [
        'JupyterLab 界面：菜单、编辑、布局'
      ],
      'Running code in the %1 kernel': ['在 %1 内核中运行代码'],
      'Running code': ['运行代码'],
      'Opening, saving or uploading files': ['打开、保存或上传文件'],
      'The terminal': ['终端'],
      'The AI assistant': ['AI 助手'],
      'An example notebook, or I am not sure': ['示例笔记本，或者我不确定'],
      'This opens a new GitHub issue with the details of this page filled in, and copies the details to the clipboard. You need a GitHub account to submit the issue.':
        [
          '这将打开一个新的 GitHub 议题并预先填入此页面的详细信息，同时将这些信息复制到剪贴板。您需要一个 GitHub 账号才能提交议题。'
        ],
      Cancel: ['取消'],
      'Continue on GitHub': ['在 GitHub 上继续']
    }
  };

  function pageConfig() {
    const node = document.getElementById('jupyter-config-data');
    return node ? JSON.parse(node.textContent) : {};
  }

  // An answer to the question, and the repository that receives the report.
  // Repositories that disable blank issues send an issue URL without a
  // template to their template chooser, so they get a template.
  function choices(context, trans) {
    let kernelRepository = 'jupyter/try-jupyter';
    if (context.kernelName === 'python') {
      kernelRepository = 'jupyterlite/pyodide-kernel';
    } else if (XEUS_KERNELS.has(context.kernelName)) {
      kernelRepository = 'jupyterlite/xeus';
    }
    return [
      context.notebookInterface
        ? {
            label: trans.__(
              'The Jupyter Notebook interface: menus, editing, layout'
            ),
            repository: 'jupyter/notebook',
            template: 'bug_report.md'
          }
        : {
            label: trans.__('The JupyterLab interface: menus, editing, layout'),
            repository: 'jupyterlab/jupyterlab',
            template: 'bug_report.md'
          },
      {
        label: context.kernelDisplayName
          ? trans.__('Running code in the %1 kernel', context.kernelDisplayName)
          : trans.__('Running code'),
        repository: kernelRepository
      },
      {
        label: trans.__('Opening, saving or uploading files'),
        repository: 'jupyterlite/jupyterlite'
      },
      { label: trans.__('The terminal'), repository: 'jupyterlite/terminal' },
      {
        label: trans.__('The AI assistant'),
        repository: 'jupyterlab/jupyter-ai-lite',
        template: 'bug_report.md'
      },
      {
        label: trans.__('An example notebook, or I am not sure'),
        repository: 'jupyter/try-jupyter'
      }
    ];
  }

  function issueBody(context) {
    const config = pageConfig();
    const versions = config.versionInfo || {};
    const version = name =>
      (versions[name] && versions[name].version) || 'unknown';
    const lab = version('@jupyterlab/application');
    const ui = context.notebookInterface
      ? `Jupyter Notebook ${version('@jupyter-notebook/application')} (JupyterLab ${lab})`
      : `JupyterLab ${lab}`;
    return [
      '## Description',
      '',
      '<!-- What did you do, what happened, and what did you expect? -->',
      '',
      '## Context',
      '',
      `- Found on: ${location.origin}${location.pathname}`,
      `- Interface: ${ui}`,
      `- Language: ${context.language}`,
      `- JupyterLite: ${config.appVersion || 'unknown'}`,
      `- Kernel: ${context.kernelDisplayName || 'none'}`,
      `- Browser: ${navigator.userAgent}`
    ].join('\n');
  }

  function issueUrl(choice, body) {
    const query = new URLSearchParams({ title: 'Try Jupyter: ', body });
    if (choice.template) {
      query.set('template', choice.template);
    }
    return `https://github.com/${choice.repository}/issues/new?${query}`;
  }

  function element(tag, className, text, css) {
    const node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text) {
      node.textContent = text;
    }
    if (css) {
      node.style.cssText = css;
    }
    return node;
  }

  // A modal dialog with the markup and classes of JupyterLab dialogs.
  // Resolves to the index of the chosen answer, or null when cancelled.
  function ask(options, trans) {
    // A modal dialog gets the size limits and the border of the browser's dialog style.
    const dialog = element(
      'dialog',
      'jp-Dialog jp-ThemedContainer',
      '',
      'max-width: none; max-height: none; border: none'
    );
    dialog.setAttribute('aria-labelledby', 'jp-TryJupyterFeedback-title');
    const form = element('form', 'jp-Dialog-content');
    form.method = 'dialog';
    const header = element(
      'div',
      'jp-Dialog-header',
      trans.__('Report a Problem')
    );
    header.id = 'jp-TryJupyterFeedback-title';
    const body = element('div', 'jp-Dialog-body', '', 'max-width: 480px');
    const fieldset = element(
      'fieldset',
      '',
      '',
      'border: none; margin: 0; padding: 0'
    );
    fieldset.appendChild(
      element(
        'legend',
        '',
        trans.__('What is the problem about?'),
        'padding: 0; margin-bottom: 8px'
      )
    );
    options.forEach((option, index) => {
      const label = element(
        'label',
        '',
        '',
        'display: flex; align-items: center; gap: 8px; margin: 6px 0'
      );
      const input = element('input');
      input.type = 'radio';
      input.name = 'try-jupyter-feedback';
      input.value = String(index);
      // A bare Enter then reports to jupyter/try-jupyter, which can triage it.
      input.checked = index === options.length - 1;
      label.append(input, option.label);
      fieldset.appendChild(label);
    });
    body.append(
      fieldset,
      element(
        'p',
        '',
        trans.__(
          'This opens a new GitHub issue with the details of this page filled in, and copies the details to the clipboard. You need a GitHub account to submit the issue.'
        ),
        'color: var(--jp-ui-font-color2)'
      )
    );
    const buttons = element('div', 'jp-Dialog-footerButtons');
    for (const [value, className, text] of [
      ['cancel', 'jp-mod-reject', trans.__('Cancel')],
      ['accept', 'jp-mod-accept', trans.__('Continue on GitHub')]
    ]) {
      const button = element(
        'button',
        `jp-Dialog-button ${className} jp-mod-styled`
      );
      button.value = value;
      button.appendChild(element('div', 'jp-Dialog-buttonLabel', text));
      buttons.appendChild(button);
    }
    const footer = element('div', 'jp-Dialog-footer');
    footer.appendChild(buttons);
    form.append(header, body, footer);
    dialog.appendChild(form);

    return new Promise(resolve => {
      dialog.addEventListener('keydown', event => {
        // The dialog is modal, so keep the shortcuts of the page out of it.
        event.stopPropagation();
        if (event.key === 'Enter' && event.target.tagName !== 'BUTTON') {
          event.preventDefault();
          dialog.close('accept');
        }
      });
      dialog.addEventListener('close', () => {
        const checked = form.querySelector('input:checked');
        dialog.remove();
        resolve(
          dialog.returnValue === 'accept' && checked
            ? Number(checked.value)
            : null
        );
      });
      document.body.appendChild(dialog);
      dialog.showModal();
      dialog.querySelector('.jp-mod-accept').focus();
    });
  }

  const plugin = {
    id: `${NAME}:plugin`,
    description:
      'Asks one question, then opens a pre-filled issue in the repository of the broken part.',
    autoStart: true,
    activate: (app, translator) => {
      translator = translator || translation.nullTranslator;
      const trans = translator.load(NAME);
      const strings = TRANSLATIONS[translator.languageCode];
      if (strings) {
        trans.loadJSON(strings, NAME);
      }
      app.commands.addCommand(COMMAND, {
        label: trans.__('Report a Problem…'),
        execute: async () => {
          const widget = app.shell.currentWidget;
          const sessionContext = widget && widget.sessionContext;
          const kernel =
            sessionContext &&
            sessionContext.session &&
            sessionContext.session.kernel;
          const context = {
            notebookInterface: !!pageConfig().notebookPage,
            language: translator.languageCode,
            kernelName: kernel ? kernel.name : null,
            kernelDisplayName: kernel
              ? sessionContext.kernelDisplayName || kernel.name
              : null
          };
          const options = choices(context, trans);
          const index = await ask(options, trans);
          if (index === null) {
            return;
          }
          const body = issueBody(context);
          // GitHub may open a template without the body for visitors who cannot write to the repository.
          if (navigator.clipboard) {
            await navigator.clipboard.writeText(body).catch(() => undefined);
          }
          window.open(issueUrl(options[index], body), '_blank', 'noopener');
        }
      });
    }
  };

  // The module federation container interface that JupyterLab loads extensions through.
  let translation;
  window._JUPYTERLAB = window._JUPYTERLAB || {};
  window._JUPYTERLAB[NAME] = {
    init: async shareScope => {
      // The application's own copy of the package holds the token of its translator.
      const [shared] = Object.values(shareScope['@jupyterlab/translation']);
      translation = (await shared.get())();
      plugin.optional = [translation.ITranslator];
    },
    get: () => Promise.resolve(() => ({ __esModule: true, default: [plugin] }))
  };
})();
