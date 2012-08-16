#ifndef MARISA_GRIMOIRE_VECTOR_H_
#define MARISA_GRIMOIRE_VECTOR_H_

#include "vector/vector.h"
#include "vector/flat-vector.h"
#include "vector/bit-vector.h"

namespace marisa {
namespace grimoire {

using vector::Vector;
typedef vector::FlatVector<MARISA_WORD_SIZE> FlatVector;
typedef vector::BitVector<MARISA_WORD_SIZE> BitVector;

}  // namespace grimoire
}  // namespace marisa

#endif  // MARISA_GRIMOIRE_VECTOR_H_
