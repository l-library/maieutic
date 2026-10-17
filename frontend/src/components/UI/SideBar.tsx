import {useState} from "react";
import * as PI from "react-icons/pi"
import * as HI from "react-icons/hi2"
import {Link} from "react-router-dom";

const SideBar = () => {
    const [sidebar, set_sidebar] = useState(false)

    const change_sidebar = () => {
        set_sidebar(!sidebar)
    }

    return (
        <div className={'border-r-2 border-border fixed h-full top-0 left-0 z-20 transition-transform duration-300 ' +
            (sidebar ? 'translate-x-0' : '-translate-x-sidebar')}>
            {/* 侧边栏本体：高度整个屏幕 */}
            <nav className={'h-full w-sidebar p-1.5 bg-sidebar'}>
                <img src="/maieutic.png" alt="maieutic"/>
                <ul className="flex flex-col gap-2">
                    <li>
                        <Link to='#' className="menu-item p-3">
                            <PI.PiPlusCircle/>
                            新对话
                        </Link>
                    </li>
                    <li>
                        <Link to='#' className={"menu-item p-3"}>
                            <PI.PiChat/>
                            全部对话
                        </Link>
                    </li>
                    <hr className={"text-border"}/>
                </ul>
            </nav>
            {/* 汉堡按钮：到顶端4刻度（16像素） 到左边68刻度 z轴位于20 圆角 字体大小xl hover时变色*/}
            <button
                className="absolute top-4 left-bar-offset z-20 rounded p-2 text-xl hover:bg-hover"
                onClick={change_sidebar}
            >
                {sidebar ? <PI.PiSidebar/> : <HI.HiBars3/>}
            </button>
        </div>
    )
}

export default SideBar