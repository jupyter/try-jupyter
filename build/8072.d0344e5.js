"use strict";(self.webpackChunk_JUPYTERLAB_CORE_OUTPUT=self.webpackChunk_JUPYTERLAB_CORE_OUTPUT||[]).push([[8072,4885],{58072:(t,e,a)=>{a.r(e),a.d(e,{default:()=>i});var n=a(10537),o=a(50082);const r={id:"@jupyterlab/mathjax2-extension:plugin",autoStart:!0,provides:a(38036).ILatexTypesetter,activate:()=>{const[t,e]=["fullMathjaxUrl","mathjaxConfig"],a=n.PageConfig.getOption(t),i=n.PageConfig.getOption(e);if(!a){const a=`${r.id} uses '${t}' and '${e}' in PageConfig to operate but '${t}' was not found.`;throw new Error(a)}return new o.MathJaxTypesetter({url:a,config:i})}},i=r}}]);
//# sourceMappingURL=8072.d0344e5.js.map