import React from 'react';

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSearch: () => void;
  showInactive: boolean;
  onToggleInactive: (show: boolean) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({
  searchQuery,
  onSearchChange,
  onSearch,
  showInactive,
  onToggleInactive,
}) => {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="d-flex align-items-center gap-2 search-bar">
      <input
        type="text"
        id="searchInput"
        className="form-control me-2"
        placeholder="Buscar por usuario o número..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <button className="btn btn-light" onClick={onSearch}>
        <i className="fas fa-search me-1"></i>Buscar
      </button>
      <div className="d-flex align-items-center gap-2 ms-3">
        <span className="text-muted small fw-semibold">Mostrar inactivos:</span>
        <div className="checkbox-wrapper-9">
          <input
            className="tgl tgl-flat"
            id="cb4-9"
            type="checkbox"
            checked={showInactive}
            onChange={(e) => onToggleInactive(e.target.checked)}
          />
          <label className="tgl-btn" htmlFor="cb4-9"></label>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;
