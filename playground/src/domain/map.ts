import type { Clanker } from './models';
export interface EstateZone { id:string; name:string; kind:string; x:number;y:number;w:number;h:number;description:string; }
export const estateZones:EstateZone[]=[
{id:'house',name:'Main house',kind:'residence',x:310,y:150,w:290,h:180,description:'East hall, reception and study. Interior rooms are grouped; no personal occupancy is tracked.'},
{id:'garden',name:'Winter garden',kind:'hospitality',x:640,y:130,w:210,h:130,description:'Illustrative garden and dinner venue. Environmental conditions are not modeled.'},
{id:'tavern',name:'Jakey’s Tavern',kind:'hospitality',x:100,y:170,w:160,h:130,description:'Wetherby’s hospitality base. Guest counts and table availability are not modeled.'},
{id:'workshop',name:'Workshop',kind:'infrastructure',x:100,y:430,w:180,h:120,description:'Cogsworth’s maintenance base. Select a clanker to inspect faults and repairs.'},
{id:'charging',name:'Charging gallery',kind:'infrastructure',x:350,y:440,w:190,h:110,description:'Clankers charging in the simulation appear here. Dock capacity and electrical circuits are not modeled.'},
{id:'service',name:'Service gallery',kind:'operations',x:650,y:400,w:190,h:140,description:'Service corridor, completed deliveries and in-transit assignments are aggregated here. Markers are symbolic, not measured positions.'},
];
export function zoneForClanker(clanker:Clanker):string|undefined {const locations:Record<string,string>={'East hall':'house',Reception:'house',Study:'house','Winter garden':'garden',"Jakey’s Tavern":'tavern',Workshop:'workshop','Charging gallery':'charging','Service corridor':'service','Service gallery':'service','Service route':'service'};return locations[clanker.location];}
