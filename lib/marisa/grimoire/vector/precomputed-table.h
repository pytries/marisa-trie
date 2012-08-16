#ifndef MARISA_GRIMOIRE_VECTOR_PRECOMPUTED_TABLE_H_
#define MARISA_GRIMOIRE_VECTOR_PRECOMPUTED_TABLE_H_

#include "../../base.h"

namespace marisa {
namespace grimoire {
namespace vector {

class PrecomputedTable {
 public:
  PrecomputedTable() {}

  std::size_t select(std::size_t i, UInt8 byte) const {
    MARISA_DEBUG_IF(i > 7, MARISA_BOUND_ERROR);
    return select_table_[i][byte];
  }

 private:
  static const UInt8 select_table_[8][256];

  PrecomputedTable(const PrecomputedTable &);
  PrecomputedTable &operator=(const PrecomputedTable &);
};

}  // namespace marisa
}  // namespace grimoire
}  // namespace vector

#endif  // MARISA_GRIMOIRE_VECTOR_PRECOMPUTED_TABLE_H_
