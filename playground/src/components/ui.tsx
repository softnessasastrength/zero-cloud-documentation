import { lazy, Suspense, useEffect, useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useStore } from '../state/store';
import { canSee, metric } from '../domain/engine';
import { clock, type Widget } from '../domain/models';
export function PageTitle({eyebrow,title,children}:{eyebrow:string;title:string;children?:ReactNode}){return <header className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1></div>{children}</header>;}
export function Field({label,children}:{label:string;children:ReactNode}){return <label className="field"><span>{label}</span>{children}</label>;}
export function Empty({children}:{children:ReactNode}){return <p className="empty">{children}</p>;}
const ChartGraphic=lazy(()=>import('./ChartView').then(module=>({default:module.ChartView})));
export function Chart(){return <Suspense fallback={<p className="empty">Loading synthetic history…</p>}><ChartGraphic/></Suspense>;}
export function DataWidget({widget}:{widget:Widget}){const simulation=useStore(s=>s.simulation);const role=useStore(s=>s.role);const [sample,setSample]=useState({value:metric({...simulation,tasks:simulation.tasks.filter(t=>canSee(t,role))},widget.source),minute:simulation.minute});useEffect(()=>{const initial=useStore.getState().simulation;setSample({value:metric({...initial,tasks:initial.tasks.filter(t=>canSee(t,role))},widget.source),minute:initial.minute});const timer=setInterval(()=>{const s=useStore.getState();setSample({value:metric({...s.simulation,tasks:s.simulation.tasks.filter(t=>canSee(t,s.role))},widget.source),minute:s.simulation.minute});},widget.refresh*1000);return()=>clearInterval(timer);},[widget.source,widget.refresh,role,simulation.seed]);return <section className={`data-widget ${widget.width}`}><div className="eyebrow">{widget.title}</div>{widget.source==='history'?<Chart/>:<Link className="metric-link" to={widget.source==='fleet'?'/fleet':'/telemetry'}><strong>{sample.value}</strong><span>{widget.source==='energy'?'kW · modeled charging load':'inspect underlying state ↗'}</span></Link>}<small>SIMULATED · sampled {clock(sample.minute)} · every {widget.refresh}s</small></section>;}
export function StatusTag({status}:{status:string}){return <span className={`status ${status}`}>{status}</span>;}
