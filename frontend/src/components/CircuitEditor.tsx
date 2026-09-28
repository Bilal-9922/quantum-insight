export default function CircuitEditor({code, setCode}: {code:string; setCode:(v:string)=>void}) {
  return <textarea className="min-h-[360px] w-full font-mono text-sm" value={code} onChange={e=>setCode(e.target.value)} />;
}
