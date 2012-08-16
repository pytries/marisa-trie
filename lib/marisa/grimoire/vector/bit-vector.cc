#include "pop-count.h"
#include "precomputed-table.h"
#include "bit-vector.h"

namespace marisa {
namespace grimoire {
namespace vector {
namespace {

std::size_t select_finish(std::size_t i, std::size_t bit_id, UInt64 unit) {
  const PopCount<64> count(unit);
  if (i < count.lo32()) {
    if (i < count.lo16()) {
      if (i >= count.lo8()) {
        bit_id += 8;
        unit >>= 8;
        i -= count.lo8();
      }
    } else if (i < count.lo24()) {
      bit_id += 16;
      unit >>= 16;
      i -= count.lo16();
    } else {
      bit_id += 24;
      unit >>= 24;
      i -= count.lo24();
    }
  } else if (i < count.lo48()) {
    if (i < count.lo40()) {
      bit_id += 32;
      unit >>= 32;
      i -= count.lo32();
    } else {
      bit_id += 40;
      unit >>= 40;
      i -= count.lo40();
    }
  } else if (i < count.lo56()) {
    bit_id += 48;
    unit >>= 48;
    i -= count.lo48();
  } else {
    bit_id += 56;
    unit >>= 56;
    i -= count.lo56();
  }
  return bit_id + PrecomputedTable().select(i, (UInt8)(unit & 0xFF));
}

}  // namespace

template <>
std::size_t BitVector<32>::rank1(std::size_t i) const {
  MARISA_DEBUG_IF(ranks_.empty(), MARISA_STATE_ERROR);
  MARISA_DEBUG_IF(i > size_, MARISA_BOUND_ERROR);

  const RankIndex &rank = ranks_[i / 512];
  std::size_t offset = rank.abs();
  switch ((i / 64) % 8) {
    case 1: {
      offset += rank.rel1();
      break;
    }
    case 2: {
      offset += rank.rel2();
      break;
    }
    case 3: {
      offset += rank.rel3();
      break;
    }
    case 4: {
      offset += rank.rel4();
      break;
    }
    case 5: {
      offset += rank.rel5();
      break;
    }
    case 6: {
      offset += rank.rel6();
      break;
    }
    case 7: {
      offset += rank.rel7();
      break;
    }
  }
  if (((i / 32) & 1) == 1) {
    offset += PopCount<32>::count(units_[(i / 32) - 1]);
  }
  offset += PopCount<32>::count(units_[i / 32] & ((1U << (i % 32)) - 1));
  return offset;
}

template <>
std::size_t BitVector<32>::select0(std::size_t i) const {
  MARISA_DEBUG_IF(select0s_.empty(), MARISA_STATE_ERROR);
  MARISA_DEBUG_IF(i >= num_0s(), MARISA_BOUND_ERROR);

  const std::size_t select_id = i / 512;
  MARISA_DEBUG_IF((select_id + 1) >= select0s_.size(), MARISA_BOUND_ERROR);
  if ((i % 512) == 0) {
    return select0s_[select_id];
  }
  std::size_t begin = select0s_[select_id] / 512;
  std::size_t end = (select0s_[select_id + 1] + 511) / 512;
  if (begin + 10 >= end) {
    while (i >= ((begin + 1) * 512) - ranks_[begin + 1].abs()) {
      ++begin;
    }
  } else {
    while (begin + 1 < end) {
      const std::size_t middle = (begin + end) / 2;
      if (i < (middle * 512) - ranks_[middle].abs()) {
        end = middle;
      } else {
        begin = middle;
      }
    }
  }
  const std::size_t rank_id = begin;
  i -= (rank_id * 512) - ranks_[rank_id].abs();

  const RankIndex &rank = ranks_[rank_id];
  std::size_t unit_id = rank_id * 16;
  if (i < (256U - rank.rel4())) {
    if (i < (128U - rank.rel2())) {
      if (i >= (64U - rank.rel1())) {
        unit_id += 2;
        i -= 64 - rank.rel1();
      }
    } else if (i < (192U - rank.rel3())) {
      unit_id += 4;
      i -= 128 - rank.rel2();
    } else {
      unit_id += 6;
      i -= 192 - rank.rel3();
    }
  } else if (i < (384U - rank.rel6())) {
    if (i < (320U - rank.rel5())) {
      unit_id += 8;
      i -= 256 - rank.rel4();
    } else {
      unit_id += 10;
      i -= 320 - rank.rel5();
    }
  } else if (i < (448U - rank.rel7())) {
    unit_id += 12;
    i -= 384 - rank.rel6();
  } else {
    unit_id += 14;
    i -= 448 - rank.rel7();
  }

  UInt32 unit = ~units_[unit_id];
  PopCount<32> count(unit);
  if (i >= count.lo32()) {
    ++unit_id;
    i -= count.lo32();
    unit = ~units_[unit_id];
    count = PopCount<32>(unit);
  }

  std::size_t bit_id = unit_id * 32;
  if (i < count.lo16()) {
    if (i >= count.lo8()) {
      bit_id += 8;
      unit >>= 8;
      i -= count.lo8();
    }
  } else if (i < count.lo24()) {
    bit_id += 16;
    unit >>= 16;
    i -= count.lo16();
  } else {
    bit_id += 24;
    unit >>= 24;
    i -= count.lo24();
  }
  return bit_id + PrecomputedTable().select(i, (UInt8)(unit & 0xFF));
}

template <>
std::size_t BitVector<32>::select1(std::size_t i) const {
  MARISA_DEBUG_IF(select1s_.empty(), MARISA_STATE_ERROR);
  MARISA_DEBUG_IF(i >= num_1s(), MARISA_BOUND_ERROR);

  const std::size_t select_id = i / 512;
  MARISA_DEBUG_IF((select_id + 1) >= select1s_.size(), MARISA_BOUND_ERROR);
  if ((i % 512) == 0) {
    return select1s_[select_id];
  }
  std::size_t begin = select1s_[select_id] / 512;
  std::size_t end = (select1s_[select_id + 1] + 511) / 512;
  if (begin + 10 >= end) {
    while (i >= ranks_[begin + 1].abs()) {
      ++begin;
    }
  } else {
    while (begin + 1 < end) {
      const std::size_t middle = (begin + end) / 2;
      if (i < ranks_[middle].abs()) {
        end = middle;
      } else {
        begin = middle;
      }
    }
  }
  const std::size_t rank_id = begin;
  i -= ranks_[rank_id].abs();

  const RankIndex &rank = ranks_[rank_id];
  std::size_t unit_id = rank_id * 16;
  if (i < rank.rel4()) {
    if (i < rank.rel2()) {
      if (i >= rank.rel1()) {
        unit_id += 2;
        i -= rank.rel1();
      }
    } else if (i < rank.rel3()) {
      unit_id += 4;
      i -= rank.rel2();
    } else {
      unit_id += 6;
      i -= rank.rel3();
    }
  } else if (i < rank.rel6()) {
    if (i < rank.rel5()) {
      unit_id += 8;
      i -= rank.rel4();
    } else {
      unit_id += 10;
      i -= rank.rel5();
    }
  } else if (i < rank.rel7()) {
    unit_id += 12;
    i -= rank.rel6();
  } else {
    unit_id += 14;
    i -= rank.rel7();
  }

  UInt32 unit = units_[unit_id];
  PopCount<32> count(unit);
  if (i >= count.lo32()) {
    ++unit_id;
    i -= count.lo32();
    unit = units_[unit_id];
    count = PopCount<32>(unit);
  }

  std::size_t bit_id = unit_id * 32;
  if (i < count.lo16()) {
    if (i >= count.lo8()) {
      bit_id += 8;
      unit >>= 8;
      i -= count.lo8();
    }
  } else if (i < count.lo24()) {
    bit_id += 16;
    unit >>= 16;
    i -= count.lo16();
  } else {
    bit_id += 24;
    unit >>= 24;
    i -= count.lo24();
  }
  return bit_id + PrecomputedTable().select(i, (UInt8)(unit & 0xFF));
}

template <>
std::size_t BitVector<64>::rank1(std::size_t i) const {
  MARISA_DEBUG_IF(ranks_.empty(), MARISA_STATE_ERROR);
  MARISA_DEBUG_IF(i > size_, MARISA_BOUND_ERROR);

  const RankIndex &rank = ranks_[i / 512];
  std::size_t offset = rank.abs();
  switch ((i / 64) % 8) {
    case 1: {
      offset += rank.rel1();
      break;
    }
    case 2: {
      offset += rank.rel2();
      break;
    }
    case 3: {
      offset += rank.rel3();
      break;
    }
    case 4: {
      offset += rank.rel4();
      break;
    }
    case 5: {
      offset += rank.rel5();
      break;
    }
    case 6: {
      offset += rank.rel6();
      break;
    }
    case 7: {
      offset += rank.rel7();
      break;
    }
  }
  offset += PopCount<64>::count(units_[i / 64] & ((1ULL << (i % 64)) - 1));
  return offset;
}

template <>
std::size_t BitVector<64>::select0(std::size_t i) const {
  MARISA_DEBUG_IF(select0s_.empty(), MARISA_STATE_ERROR);
  MARISA_DEBUG_IF(i >= num_0s(), MARISA_BOUND_ERROR);

  const std::size_t select_id = i / 512;
  MARISA_DEBUG_IF((select_id + 1) >= select0s_.size(), MARISA_BOUND_ERROR);
  if ((i % 512) == 0) {
    return select0s_[select_id];
  }
  std::size_t begin = select0s_[select_id] / 512;
  std::size_t end = (select0s_[select_id + 1] + 511) / 512;
  if (begin + 10 >= end) {
    while (i >= ((begin + 1) * 512) - ranks_[begin + 1].abs()) {
      ++begin;
    }
  } else {
    while (begin + 1 < end) {
      const std::size_t middle = (begin + end) / 2;
      if (i < (middle * 512) - ranks_[middle].abs()) {
        end = middle;
      } else {
        begin = middle;
      }
    }
  }
  const std::size_t rank_id = begin;
  i -= (rank_id * 512) - ranks_[rank_id].abs();

  const RankIndex &rank = ranks_[rank_id];
  std::size_t unit_id = rank_id * 8;
  if (i < (256U - rank.rel4())) {
    if (i < (128U - rank.rel2())) {
      if (i >= (64U - rank.rel1())) {
        unit_id += 1;
        i -= 64 - rank.rel1();
      }
    } else if (i < (192U - rank.rel3())) {
      unit_id += 2;
      i -= 128 - rank.rel2();
    } else {
      unit_id += 3;
      i -= 192 - rank.rel3();
    }
  } else if (i < (384U - rank.rel6())) {
    if (i < (320U - rank.rel5())) {
      unit_id += 4;
      i -= 256 - rank.rel4();
    } else {
      unit_id += 5;
      i -= 320 - rank.rel5();
    }
  } else if (i < (448U - rank.rel7())) {
    unit_id += 6;
    i -= 384 - rank.rel6();
  } else {
    unit_id += 7;
    i -= 448 - rank.rel7();
  }

  return select_finish(i, unit_id * 64, ~units_[unit_id]);
}

template <>
std::size_t BitVector<64>::select1(std::size_t i) const {
  MARISA_DEBUG_IF(select1s_.empty(), MARISA_STATE_ERROR);
  MARISA_DEBUG_IF(i >= num_1s(), MARISA_BOUND_ERROR);

  const std::size_t select_id = i / 512;
  MARISA_DEBUG_IF((select_id + 1) >= select1s_.size(), MARISA_BOUND_ERROR);
  if ((i % 512) == 0) {
    return select1s_[select_id];
  }
  std::size_t begin = select1s_[select_id] / 512;
  std::size_t end = (select1s_[select_id + 1] + 511) / 512;
  if (begin + 10 >= end) {
    while (i >= ranks_[begin + 1].abs()) {
      ++begin;
    }
  } else {
    while (begin + 1 < end) {
      const std::size_t middle = (begin + end) / 2;
      if (i < ranks_[middle].abs()) {
        end = middle;
      } else {
        begin = middle;
      }
    }
  }
  const std::size_t rank_id = begin;
  i -= ranks_[rank_id].abs();

  const RankIndex &rank = ranks_[rank_id];
  std::size_t unit_id = rank_id * 8;
  if (i < rank.rel4()) {
    if (i < rank.rel2()) {
      if (i >= rank.rel1()) {
        unit_id += 1;
        i -= rank.rel1();
      }
    } else if (i < rank.rel3()) {
      unit_id += 2;
      i -= rank.rel2();
    } else {
      unit_id += 3;
      i -= rank.rel3();
    }
  } else if (i < rank.rel6()) {
    if (i < rank.rel5()) {
      unit_id += 4;
      i -= rank.rel4();
    } else {
      unit_id += 5;
      i -= rank.rel5();
    }
  } else if (i < rank.rel7()) {
    unit_id += 6;
    i -= rank.rel6();
  } else {
    unit_id += 7;
    i -= rank.rel7();
  }

  return select_finish(i, unit_id * 64, units_[unit_id]);
}

template <std::size_t T>
void BitVector<T>::build_index(const BitVector &bv,
    bool enables_select0, bool enables_select1) {
  ranks_.resize((bv.size() / 512) + (((bv.size() % 512) != 0) ? 1 : 0) + 1);

  std::size_t num_0s = 0;
  std::size_t num_1s = 0;

  for (std::size_t i = 0; i < bv.size(); ++i) {
    if ((i % 64) == 0) {
      const std::size_t rank_id = i / 512;
      switch ((i / 64) % 8) {
        case 0: {
          ranks_[rank_id].set_abs(num_1s);
          break;
        }
        case 1: {
          ranks_[rank_id].set_rel1(num_1s - ranks_[rank_id].abs());
          break;
        }
        case 2: {
          ranks_[rank_id].set_rel2(num_1s - ranks_[rank_id].abs());
          break;
        }
        case 3: {
          ranks_[rank_id].set_rel3(num_1s - ranks_[rank_id].abs());
          break;
        }
        case 4: {
          ranks_[rank_id].set_rel4(num_1s - ranks_[rank_id].abs());
          break;
        }
        case 5: {
          ranks_[rank_id].set_rel5(num_1s - ranks_[rank_id].abs());
          break;
        }
        case 6: {
          ranks_[rank_id].set_rel6(num_1s - ranks_[rank_id].abs());
          break;
        }
        case 7: {
          ranks_[rank_id].set_rel7(num_1s - ranks_[rank_id].abs());
          break;
        }
      }
    }

    if (bv[i]) {
      if (enables_select1 && ((num_1s % 512) == 0)) {
        select1s_.push_back(i);
      }
      ++num_1s;
    } else {
      if (enables_select0 && ((num_0s % 512) == 0)) {
        select0s_.push_back(i);
      }
      ++num_0s;
    }
  }

  if ((bv.size() % 512) != 0) {
    const std::size_t rank_id = (bv.size() - 1) / 512;
    switch (((bv.size() - 1) / 64) % 8) {
      case 0: {
        ranks_[rank_id].set_rel1(num_1s - ranks_[rank_id].abs());
      }
      case 1: {
        ranks_[rank_id].set_rel2(num_1s - ranks_[rank_id].abs());
      }
      case 2: {
        ranks_[rank_id].set_rel3(num_1s - ranks_[rank_id].abs());
      }
      case 3: {
        ranks_[rank_id].set_rel4(num_1s - ranks_[rank_id].abs());
      }
      case 4: {
        ranks_[rank_id].set_rel5(num_1s - ranks_[rank_id].abs());
      }
      case 5: {
        ranks_[rank_id].set_rel6(num_1s - ranks_[rank_id].abs());
      }
      case 6: {
        ranks_[rank_id].set_rel7(num_1s - ranks_[rank_id].abs());
        break;
      }
    }
  }

  size_ = bv.size();
  num_1s_ = bv.num_1s();

  ranks_.back().set_abs(num_1s);
  if (enables_select0) {
    select0s_.push_back(bv.size());
    select0s_.shrink();
  }
  if (enables_select1) {
    select1s_.push_back(bv.size());
    select1s_.shrink();
  }
}

template void BitVector<32>::build_index(const BitVector &bv,
    bool enables_select0, bool enables_select1);
template void BitVector<64>::build_index(const BitVector &bv,
    bool enables_select0, bool enables_select1);

}  // namespace vector
}  // namespace grimoire
}  // namespace marisa
