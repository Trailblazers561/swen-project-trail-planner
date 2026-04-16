import Navbar from "./components/Navbar";

function Privileges() {
  return (
    <div className="flex flex-col">
      <Navbar />

      <div className="filter-group w-full bg-[var(--color-button-secondary)]">
        <div className="font-semibold text-2xl p-2 ml-2 text-left">
          Privilege Management
        </div>
      </div>

      <div>hello, world!</div>
    </div>
  );
}

export default Privileges;