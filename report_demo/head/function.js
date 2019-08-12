var div_state=0;
function isArray(obj) {
return Object.prototype.toString.call(obj) === '[object Array]'
}

function isHasElement(arr,value){
    var str=arr.toString(),index=str.indexOf(value)
    if(index >= 0){
        var reg1=new RegExp("((^|,)"+value+"(,|$))","gi")
        return str.replace(reg1,"$2@$3").replace(/[^,@]/g,"").indexOf("@")
    }else{
        return -1
    }
}

function accAdd(arg1, arg2) {
    var r1, r2, m, c;
    try {
        r1 = arg1.toString().split(".")[1].length;
    }
    catch (e) {
        r1 = 0;
    }
    try {
        r2 = arg2.toString().split(".")[1].length;
    }
    catch (e) {
        r2 = 0;
    }
    c = Math.abs(r1 - r2);
    m = Math.pow(10, Math.max(r1, r2));
    if (c > 0) {
        var cm = Math.pow(10, c);
        if (r1 > r2) {
            arg1 = Number(arg1.toString().replace(".", ""));
            arg2 = Number(arg2.toString().replace(".", "")) * cm;
        } else {
            arg1 = Number(arg1.toString().replace(".", "")) * cm;
            arg2 = Number(arg2.toString().replace(".", ""));
        }
    } else {
        arg1 = Number(arg1.toString().replace(".", ""));
        arg2 = Number(arg2.toString().replace(".", ""));
    }
    return (arg1 + arg2) / m;
}

Number.prototype.add = function (arg) {
    return accAdd(arg, this);
};

function decimal(num,v){
    var vv=Math.pow(10,v)
    return Math.round(num*vv)/vv
}

function accSub(arg1, arg2) {
    var r1, r2, m, n;
    try {
        r1 = arg1.toString().split(".")[1].length;
    }
    catch (e) {
        r1 = 0;
    }
    try {
        r2 = arg2.toString().split(".")[1].length;
    }
    catch (e) {
        r2 = 0;
    }
    m = Math.pow(10, Math.max(r1, r2));
    n = (r1 >= r2) ? r1 : r2;
    return ((arg1 * m - arg2 * m) / m).toFixed(n);
}

Number.prototype.sub = function (arg) {
    return accSub(this, arg);
};

function accMul(arg1,arg2){
    var m=0,s1=arg1.toString(),s2=arg2.toString()
    try {m += s1.split(".")[1].length;}
    catch (e){}
    try {m += s2.split(".")[1].length;}
    catch (e){}
    return Number(s1.replace(".","")) * Number(s2.replace(".","")) / Math.pow(10,m)
}

Number.prototype.mul=function (arg){return accMul(arg, this)}

function accDiv(arg1,arg2){
    var t1=0,t2=0,r1,r2;
    try {t1=arg1.toString().split(".")[1].length}
    catch (e){}
    try {t2=arg2.toString().split(".")[1].length}
    catch (e){}
    with (Math){
        r1=Number(arg1.toString().replace(".",""))
        r2=Number(arg2.toString().replace(".",""))
        return (r1/r2)*Math.pow(10,t2-t1)
    }
}

Number.prototype.div=function (arg){return accDiv(this,arg)}