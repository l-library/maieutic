import SideBar from '@/components/UI/SideBar'
import {Chat} from "@/components/UI/Chat.tsx";

const Home = () => {
    // TODO: header
    return (
        <div className="flex flex-col">
            <SideBar/>
            <Chat conversation_id={1}/>
        </div>
    )
}

export default Home