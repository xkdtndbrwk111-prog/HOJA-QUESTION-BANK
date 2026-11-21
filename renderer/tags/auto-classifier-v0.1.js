/* HOJA Render Tags v0.1 — prospective semantic classifier.
 * Reference helper for NEW question creation. The 183 YBM tags are saved separately,
 * teacher review remains required, and this does not change approved cartridges.
 *
 * Usage (Node): const {classifyQuestion}=require('./auto-classifier-v0.1.js');
 *   console.log(classifyQuestion(question));
 * Browser: window.HojaTagClassifier.classifyQuestion(question);
 */
(function(root){
  "use strict";
  function imageInfo(asset,position,alt,prompt){
    const src=String(asset||"").toLowerCase();
    const desc=String(alt||"")+" "+String(prompt||"");
    let kind="general",subtype="scene";
    if(/graph|chart|graph_|그래프|표[를의]|연표|timeline|statistics|table/.test(src+" "+desc)){kind="chart";subtype=/timeline|연표/.test(src+" "+desc)?"timeline":/table|표[를의]/.test(src+" "+desc)?"table":"graph";}
    else if(/polygon|triangle|angle|geometry|shape|net_|도형|각도|꼭짓점|전개도/.test(src+" "+desc)){kind="geometry";subtype="shape";}
    else if(/map|wayfinding|directions|route|street|지도|길찾기|위치|건물.*거리/.test(src+" "+desc)){kind="informational";subtype=/route|directions|길찾기/.test(src+" "+desc)?"wayfinding":"map";}
    else if(/scientific|experiment|실험|구조도|회로|현미경|실험장치/.test(src+" "+desc)){kind="informational";subtype="scientific_diagram";}
    else if(/object|thing|물건|사물/.test(src+" "+desc))subtype="object";
    const fine=kind!=="general";
    return {asset:String(asset),position,kind,subtype,needsFineDetail:fine,priority:fine?"high":"normal"};
  }
  function classifyQuestion(q){
    if(!q||typeof q!=="object")throw new TypeError("question object required");
    const prompt=String(q.prompt||q.question||"");
    const images=[];
    if(q.image)images.push(imageInfo(q.image,"question",q.imageAlt,prompt));
    for(const choice of q.choices||[])if(choice.image)images.push(imageInfo(choice.image,"choice",choice.imageAlt,prompt));
    const hasExplicitDialogue=Array.isArray(q.dialogue)&&q.dialogue.some(t=>t&&t.speaker);
    const hasInlineDialogue=/(?:^|[\n\s])(?:A|B|Girl|Boy|Teacher|Student|Mom|Dad)\s*[:：]/m.test(prompt);
    const hasDialogue=hasExplicitDialogue||hasInlineDialogue;
    const lines=prompt.split(/\n+/).map(x=>x.trim()).filter(Boolean);
    const tail=lines.slice(1).join(" ");
    const reading=tail.length>=45 || /다음\s*(글|이야기|내용|자료)를?\s*읽고/.test(prompt);
    const ex=lines.length>1 && tail.length>0 && !reading;
    const texts=["question"];
    if(/고르세요|쓰세요|읽고|보고|따라|완성|찾으세요|구하세요|알맞은/.test(prompt))texts.push("instruction");
    if(hasDialogue)texts.push("dialogue");
    if(reading)texts.push("reading");
    if(ex)texts.push("example_sentence");
    if(/\([가-힣]\)/.test(prompt))texts.push("list");
    texts.push("choices");
    const fine=images.some(x=>x.needsFineDetail);
    const hasInformation=images.some(x=>x.kind==="informational"||x.kind==="chart"||x.kind==="geometry");
    let family="text_auto",hint=null;
    if(hasDialogue&&hasInformation){family="dialogue_informational";hint="dialogue-image";}
    else if(hasDialogue){family="dialogue_stack";hint="dialogue-stack";}
    else if(images.some(x=>x.position==="choice")){family="visual_choices";}
    else if(hasInformation){family="informational_split";hint="map";}
    else if(reading){family="reading_stack";hint="reading-stack";}
    else if(ex){family="text_stack";hint="stack";}
    else if(images.length){family="scene_auto";}
    const uncertain=hasInlineDialogue || images.some(x=>x.kind==="general" && /지도|그래프|도형|실험|눈금/.test(prompt));
    const imagePriority=fine?"high":images.length?"medium":"low";
    return {
      schemaVersion:"0.1.0-draft",questionId:String(q.id||q.questionId||""),
      questionType:q.type||"MCQ",images,texts,
      constraints:{speakerTurnsVertical:hasDialogue,preserveOriginalText:true,minimumImageDetail:fine?"high":"normal",
        elementPriority:{question:"medium",reading:reading?"high":"low",dialogue:hasDialogue?"high":"low",image:imagePriority,choices:"medium"}},
      layout:{recommendedFamily:family,rendererHint:hint,selectionBasis:"semantic tags; DOM fit/overlap checks required",teacherPreference:null},
      confidence:uncertain?"medium":"high",needsHumanReview:uncertain,
      evidence:["Automatic semantic inference; not teacher-approved"].concat(uncertain?["Check inferred dialogue or information graphic manually"]:[])
    };
  }
  const api={classifyQuestion,imageInfo};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HojaTagClassifier=api;
})(typeof window!=="undefined"?window:undefined);
