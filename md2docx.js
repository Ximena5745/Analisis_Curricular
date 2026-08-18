const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  PageBreak, Header, Footer, PageNumber, ImageRun
} = require("docx");

// Rutas relativas a la ubicación de este script.
// Uso:  npm install docx   (una sola vez)  →  node md2docx.js
const BASE = __dirname;
const MD  = path.join(BASE, "articulo_curricular_IA.md");
const OUT = path.join(BASE, "articulo_curricular_IA.docx");
const IMGDIR = path.join(BASE, "data", "output");
const AZUL="1a3a5c", AZULCLA="2d7dd2", TXT="1a1a1a", FONT="Times New Roman";

function inline(text, base={}) {
  const runs=[]; const re=/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g; let last=0,m;
  const push=(t,o)=>{ if(t) runs.push(new TextRun({text:t,font:FONT,size:24,color:TXT,...base,...o})); };
  while((m=re.exec(text))!==null){
    push(text.slice(last,m.index)); const tok=m[0];
    if(tok.startsWith("**")) push(tok.slice(2,-2),{bold:true});
    else if(tok.startsWith("`")) push(tok.slice(1,-1),{font:"Consolas",size:21,color:"1F4E79"});
    else push(tok.slice(1,-1),{italics:true});
    last=m.index+tok.length;
  }
  push(text.slice(last));
  return runs.length?runs:[new TextRun({text:"",font:FONT,size:24})];
}
const H=(t,l)=>new Paragraph({children:inline(t,{bold:true,color:AZUL,size:l===1?32:l===2?27:25}),
  heading:l===1?HeadingLevel.HEADING_1:l===2?HeadingLevel.HEADING_2:HeadingLevel.HEADING_3,
  spacing:{before:l===1?300:200,after:l===1?120:90},keepNext:true,keepLines:true});
const BULLET=t=>new Paragraph({children:inline(t),bullet:{level:0},alignment:AlignmentType.JUSTIFIED,spacing:{after:50,line:284}});
const CODE=t=>(!t||!t.trim())?null:new Paragraph({children:[new TextRun({text:t,font:"Consolas",size:20,color:"1F4E79"})],
  shading:{type:ShadingType.CLEAR,fill:"F2F6FA"},spacing:{after:10,line:240},indent:{left:340}});

const BOX=t=>new Paragraph({children:inline(t,{size:22}),alignment:AlignmentType.JUSTIFIED,
  spacing:{before:140,after:140,line:280},indent:{left:280,right:200},
  shading:{type:ShadingType.CLEAR,fill:"EAF3FA"},
  border:{left:{style:BorderStyle.SINGLE,size:20,color:"2d7dd2",space:10},
          top:{style:BorderStyle.SINGLE,size:2,color:"EAF3FA",space:6},
          bottom:{style:BorderStyle.SINGLE,size:2,color:"EAF3FA",space:6},
          right:{style:BorderStyle.SINGLE,size:2,color:"EAF3FA",space:6}}});
const SPACER=()=>null;   // sin párrafos vacíos: el espaciado va en los estilos
const HR=()=>new Paragraph({children:[new TextRun("")],border:{bottom:{style:BorderStyle.SINGLE,size:6,color:"C8D8E4",space:6}},spacing:{before:120,after:160}});

function mkTable(headers, rows){
  const n=headers.length, total=9020, w=Math.floor(total/n);
  const cell=(txt,isH,al)=>new TableCell({
    children:[new Paragraph({children:inline(String(txt).trim(),isH?{bold:true,color:"FFFFFF",size:21}:{size:21}),
      alignment:al==="c"?AlignmentType.CENTER:AlignmentType.LEFT,spacing:{before:50,after:50}})],
    shading:{type:ShadingType.CLEAR,fill:isH?AZULCLA:"FFFFFF"},
    width:{size:w,type:WidthType.DXA},margins:{top:60,bottom:60,left:90,right:90}});
  return new Table({
    rows:[new TableRow({children:headers.map(h=>cell(h,true,"c")),tableHeader:true}),
      ...rows.map(r=>new TableRow({children:r.map((c,j)=>cell(c,false,j===0?"l":"c"))}))],
    width:{size:total,type:WidthType.DXA},columnWidths:new Array(n).fill(w),
    borders:{top:{style:BorderStyle.SINGLE,size:4,color:"9DC3E6"},bottom:{style:BorderStyle.SINGLE,size:4,color:"9DC3E6"},
      left:{style:BorderStyle.SINGLE,size:4,color:"9DC3E6"},right:{style:BorderStyle.SINGLE,size:4,color:"9DC3E6"},
      insideHorizontal:{style:BorderStyle.SINGLE,size:2,color:"C8D8E4"},insideVertical:{style:BorderStyle.SINGLE,size:2,color:"C8D8E4"}}});
}
function img(file,w,h){
  const p=path.join(IMGDIR,file);
  if(!fs.existsSync(p)) return new Paragraph({children:inline("[Figura no encontrada: "+file+"]",{italics:true,color:"888888"}),alignment:AlignmentType.CENTER});
  return new Paragraph({children:[new ImageRun({type:"png",data:fs.readFileSync(p),transformation:{width:w,height:h},
    altText:{title:file,description:file,name:file}})],alignment:AlignmentType.CENTER,spacing:{before:140,after:60}});
}
const CAPTION=t=>new Paragraph({children:[new TextRun({text:t,font:FONT,size:20,italics:true,color:"666666"})],
  alignment:AlignmentType.CENTER,spacing:{after:200}});

const FIGS={
 "1":["fig1_heatmap_variables_sede.png",520,330,"Figura 1. Heatmap de variables curriculares por sede"],
 "2":["fig2_evaluabilidad_programas.png",500,380,"Figura 2. Evaluabilidad (V3) por programa"],
 "3":["fig3_trazabilidad_sede.png",500,320,"Figura 3. Distribución de trazabilidad (V4) por sede"],
 "4":["fig4_tipos_saber.png",380,300,"Figura 4. Distribución de RA por tipo de saber (N=586)"],
 "5":["fig5_verbos_competencias.png",520,320,"Figura 5. Verbos más frecuentes en competencias (V2)"],
 "6":["fig6_radar_variables.png",420,400,"Figura 6. Radar del perfil de variables curriculares"],
 "7":["fig7_correlacion_spearman.png",500,410,"Figura 7. Matriz de correlación de Spearman entre variables (n=50)"],
 "8":["fig8_kruskal_sedes.png",560,250,"Figura 8. Distribución de V3, V4 y V5 por sede (Kruskal-Wallis)"],
 "9":["fig9_asignaturas_compartidas.png",560,215,"Figura 9. Consistencia de contenido y oportunidades de homologación entre asignaturas"],
 "10":["fig10_tendencias.png",520,280,"Figura 10. Presencia de tendencias globales: amplitud frente a profundidad"],
 "11":["fig11_cobertura_perfil.png",520,260,"Figura 11. Cobertura del perfil de egreso por campo"],
 "12":["fig12_auditoria_score.png",560,215,"Figura 12. Auditoría del score académico: ausencia de sesgo disciplinar y efecto del umbral inactivo"],
};

const raw=fs.readFileSync(MD,"utf8").split(/\r?\n/);
const body=[]; let i=0;

body.push(new Paragraph({children:[new TextRun({text:"La inteligencia artificial generativa como infraestructura de decisión curricular",bold:true,size:32,color:AZUL,font:FONT})],alignment:AlignmentType.CENTER,spacing:{after:100}}));
body.push(new Paragraph({children:[new TextRun({text:"Coherencia, evaluabilidad y trazabilidad en el diseño curricular de educación superior",size:24,color:"44688a",font:FONT,italics:true})],alignment:AlignmentType.CENTER,spacing:{after:80}}));
body.push(new Paragraph({children:[new TextRun({text:"Estudio mixto sobre 50 matrices curriculares · 39 programas · 5 sedes",size:21,color:"555555",font:FONT})],alignment:AlignmentType.CENTER,spacing:{after:260},
  border:{bottom:{style:BorderStyle.SINGLE,size:6,color:"C8D8E4",space:8}}}));

while(i<raw.length){
  const t=raw[i].trim();
  if(/^---+$/.test(t)){ i++; continue; }
  if(/^#{1,6}\s/.test(t)){
    const lvl=t.match(/^#+/)[0].length, txt=t.replace(/^#+\s*/,"");
    if(lvl===1){ i++; continue; }
    if(lvl===2){ body.push(H(txt,1)); }
    else if(lvl===3) body.push(H(txt,2));
    else body.push(H(txt,3));
    i++; continue;
  }
  if(t.startsWith("```")){ i++; while(i<raw.length&&!raw[i].trim().startsWith("```")){ const c=CODE(raw[i]); if(c) body.push(c); i++; } i++;  continue; }
  if(t.startsWith("|")&&i+1<raw.length&&/^\|[\s:|-]+\|$/.test(raw[i+1].trim())){
    const sp=l=>l.trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(c=>c.trim());
    const headers=sp(raw[i]); i+=2; const rows=[];
    while(i<raw.length&&raw[i].trim().startsWith("|")){ rows.push(sp(raw[i])); i++; }
    body.push(mkTable(headers,rows));  continue;
  }
  if(t.startsWith("> ")){ body.push(BOX(t.slice(2))); i++; continue; }
  if(/^[-*]\s+/.test(t)){ body.push(BULLET(t.replace(/^[-*]\s+/,""))); i++; continue; }
  if(/^\*\(Ver Figura \d+/.test(t)){
    const seen=new Set();
    for(const mm of t.matchAll(/Figura (\d+)/g)){
      const n=mm[1]; if(seen.has(n)||!FIGS[n]) continue; seen.add(n);
      const f=FIGS[n]; body.push(img(f[0],f[1],f[2])); body.push(CAPTION(f[3]));
    }
    i++; continue;
  }
  if(t===""){ i++; continue; }
  const isTT=/^\*\*(Tabla|Figura) /.test(t);
  body.push(new Paragraph({children:inline(t),alignment:AlignmentType.JUSTIFIED,spacing:{after:isTT?60:110,line:288},keepNext:isTT}));
  i++;
}

const doc=new Document({
  creator:"Análisis Curricular",
  title:"IAg como infraestructura de decisión curricular",
  styles:{default:{document:{run:{font:FONT,size:24,color:TXT}}}},
  sections:[{
    properties:{page:{size:{width:11906,height:16838},margin:{top:1440,right:1440,bottom:1440,left:1440}}},
    headers:{default:new Header({children:[new Paragraph({children:[new TextRun({text:"IAg como infraestructura de decisión curricular",size:17,color:"8899aa",font:FONT})],alignment:AlignmentType.RIGHT,border:{bottom:{style:BorderStyle.SINGLE,size:4,color:"C8D8E4",space:4}}})]})},
    footers:{default:new Footer({children:[new Paragraph({children:[new TextRun({children:[PageNumber.CURRENT],size:18,color:"8899aa",font:FONT})],alignment:AlignmentType.CENTER})]})},
    children:body.filter(Boolean),
  }],
});
Packer.toBuffer(doc).then(b=>{ fs.writeFileSync(OUT,b); console.log("DOCX generado:",(b.length/1024).toFixed(0)+" KB"); });
