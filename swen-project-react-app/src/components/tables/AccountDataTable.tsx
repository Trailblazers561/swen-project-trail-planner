import { UserRow } from "./UserDataTable";
import DataTable, { TableColumn } from "react-data-table-component";{}

interface Props {
    data: UserRow[];
    //loading: boolean;
}

const columns: TableColumn<UserRow>[] = [
    {
            name: "Username",
            selector: (row) => row.username, //row is a UserRow instance
            sortable: true,
            grow: 2,
        }
] 

const AccountDataTable: React.FC<Props> = ({ data }) => {

    // interface usernameRow {
    //     text: string;
    //     username: string;
    // }

    // const usernamerow = usernameRow

    return(
        <div className="bg-gray-50 shadow-md modal-overlay" data-testid="device-log-table">
            <DataTable
            columns = {columns}
            data = {data}
            // progressPending = {loading}
            />
        </div>
    )
}

export default AccountDataTable