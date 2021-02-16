import { Neptune, SetG, G } from "./neptune/skeleton/neptune";

const {ccclass, property} = cc._decorator;


@ccclass
export default class Helloworld extends cc.Component {

    @property(cc.Label)
    label: cc.Label = null;

    @property
    text: string = 'hellox';

    start () {
        // init logic
        this.label.string = this.text;
        SetG(new Neptune());
        G().init();
    }

    update(dt: number) {
        
    } 
}
