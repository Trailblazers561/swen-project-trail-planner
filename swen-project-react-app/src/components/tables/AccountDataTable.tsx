import { useState } from "react";
import { UserRow } from "./UserDataTable";
import DataTable, { TableColumn } from "react-data-table-component";import { UserRole } from "@/lib/apiTypes";
{}

interface Props {
    data: UserRow[];
    onClose?: () => void;
    //loading: boolean;
}

interface textRow {
        text: string;
        field: string;
    }

const columns: TableColumn<textRow>[] = [
    {
        selector: (row) => row.text, //row is a textRow instance
        // grow: 2,
    },
    {
        selector: (row) => row.field
    }
] 

const AccountDataTable: React.FC<Props> = ({ data, onClose }) => {

    const selectedUser:UserRow = data[0];
    console.log(selectedUser);
    // const previousUser:UserRow = {username: "", email: "", banned: false, user_id: "", role: ""};

    const [bannedText, setBannedText] = useState<string>("No");
    const [textData, setTextData] = useState<Array<textRow>>([]);
        
    
    // if (selectedUser.banned) {
    //     setBannedText("Yes")
    // }
    // else {
    //     setBannedText("No")
    // }

    const loadData = () => {

        if (selectedUser != null) {
            const usernamerow:textRow = {text: "Username", field: selectedUser.username};
            const rolerow:textRow = {text: "Role", field: selectedUser.role.toString()};
            const bannedrow:textRow = {text: "Banned?", field: bannedText};
            const emailrow:textRow = {text: "Email", field: selectedUser.email}

            setTextData([usernamerow, rolerow, bannedrow, emailrow]);
        }

        else {
            setTextData([]);
        }
    }

    

    return(
        <div className="bg-gray-50 shadow-md modal-overlay w-screen h-screen" data-testid="device-log-table">
            <button className="modal-close" onClick={onClose}>x</button>
            <DataTable
            columns = {columns}
            data = {textData}
            // progressPending = {loading}
            />
        </div>
    )
}

export default AccountDataTable